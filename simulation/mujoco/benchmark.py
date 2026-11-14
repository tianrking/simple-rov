"""Deterministic scenario evaluation at 50 Hz control; no claim of physical accuracy."""

from pathlib import Path
import argparse, csv, hashlib, json, time
import numpy as np
from environment import ROV, S


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seconds", type=float, default=8)
    p.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    p.add_argument("--output-dir", type=Path, default=S.parents[1] / "runs/benchmark")
    p.add_argument(
        "--publish",
        action="store_true",
        help="Write verified digital benchmark summary to validation/",
    )
    args = p.parse_args()
    if not np.isfinite(args.seconds) or args.seconds < 4:
        raise ValueError("Benchmark needs at least 4 seconds")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    cases = []
    traces = []
    wall = time.perf_counter()
    for scenario in [
        "pool",
        "seawater",
        "cross-current",
        "tethered",
        "motor-fault",
        "native-fluid",
    ]:
        for seed in args.seeds:
            env = ROV(scenario=scenario, seed=seed)
            env.reset(roll=0.12, yaw=-0.2)
            dt = env.model.opt.timestep
            stride = round(0.02 / dt)
            trace = []
            effort = 0.0
            for tick in range(round(args.seconds / dt)):
                t = env.data.time
                target = 1.2 if t < 2 else 1.0
                surge = 1.0 if 3 <= t < 5 else 0.0
                if tick % stride == 0:
                    command = env.controller(
                        depth=target,
                        surge_N=surge,
                        yaw=0.3,
                        measurement=env.measurements(),
                    )
                pos, rpy, _, _ = env.step(command)
                effort += float(env.force @ env.force) * dt
                if tick % stride == 0:
                    error = np.arctan2(np.sin(rpy[2] - 0.3), np.cos(rpy[2] - 0.3))
                    trace.append(
                        [
                            float(env.data.time),
                            float(-pos[2]),
                            target,
                            float(rpy[0]),
                            float(error),
                            float(pos[1]),
                            env.diagnostics["tether_tension_N"],
                            env.allocator.last["weighted_residual_norm"],
                        ]
                    )
            a = np.asarray(trace)
            tail = a[a[:, 0] >= args.seconds - 2]
            case = {
                "scenario": scenario,
                "seed": seed,
                "depth_RMSE_last2s_m": float(
                    np.sqrt(np.mean((tail[:, 1] - tail[:, 2]) ** 2))
                ),
                "yaw_RMSE_last2s_rad": float(np.sqrt(np.mean(tail[:, 4] ** 2))),
                "roll_RMSE_last2s_rad": float(np.sqrt(np.mean(tail[:, 3] ** 2))),
                "lateral_drift_m": float(a[-1, 5]),
                "effort_N2_s": effort,
                "max_tether_tension_N": float(a[:, 6].max()),
                "max_allocation_residual": float(a[:, 7].max()),
                "controlled_rank": env.allocator.last["rank"],
                "finite": bool(np.isfinite(a).all()),
            }
            assert case["finite"]
            # These are uncalibrated software regression envelopes, never real-vehicle requirements.
            if scenario != "motor-fault":
                assert (
                    case["depth_RMSE_last2s_m"] < 0.08
                    and case["yaw_RMSE_last2s_rad"] < 0.15
                    and case["roll_RMSE_last2s_rad"] < 0.12
                ), case
            else:
                assert (
                    case["controlled_rank"] == 3 and case["max_allocation_residual"] > 0
                )
            cases.append(case)
            name = f"{scenario}-seed{seed}.csv"
            with (args.output_dir / name).open("w", newline="") as f:
                w = csv.writer(f)
                w.writerow(
                    [
                        "time_s",
                        "depth_m",
                        "target_depth_m",
                        "roll_rad",
                        "yaw_error_rad",
                        "y_m",
                        "tether_tension_N",
                        "weighted_allocation_residual",
                    ]
                )
                w.writerows(trace)
            if seed == args.seeds[0]:
                traces.append((scenario, a))
    metadata = ROV().metadata()
    report = {
        "engine_version": metadata["engine_version"],
        "physics_timestep_s": 0.002,
        "control_period_s": 0.02,
        "duration_each_s": args.seconds,
        "seeds": args.seeds,
        "cases": cases,
        "wall_seconds": time.perf_counter() - wall,
        "source_sha256": metadata["source_sha256"]
        | {"benchmark.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        "scope": "Seeded software scenario regression under assumed coefficients. Fault case is rank-deficient; position hold is not a requirement. Native-fluid envelope is an assumed ellipsoid. No physical calibration or optimality claim.",
        "passed": True,
    }
    (args.output_dir / "benchmark.json").write_text(json.dumps(report, indent=2) + "\n")
    if args.publish:
        (S.parents[1] / "validation/simulation_benchmark.json").write_text(
            json.dumps(report, indent=2) + "\n"
        )
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(2, 2, figsize=(12, 7.5), layout="constrained")
        for label, a in traces:
            for ax, y in zip(
                axes.flat, [a[:, 1], np.rad2deg(a[:, 4]), a[:, 5], a[:, 6]]
            ):
                ax.plot(a[:, 0], y, label=label, lw=1.4)
        axes[0, 0].plot(
            traces[0][1][:, 0],
            traces[0][1][:, 2],
            color="black",
            ls="--",
            label="depth target",
        )
        for ax, title, unit in zip(
            axes.flat,
            [
                "Depth response",
                "Heading error",
                "Lateral drift (not controlled)",
                "Lumped tether tension",
            ],
            ["m", "deg", "m", "N"],
        ):
            ax.set(title=title, xlabel="Simulation time [s]", ylabel=unit)
            ax.grid(alpha=0.2)
        axes[0, 0].legend(fontsize=8, ncol=2)
        fig.suptitle(
            "SimpleROV | Seeded scenario benchmark\nUncalibrated parameters; curves are software examples",
            fontsize=14,
        )
        fig.savefig(args.output_dir / "benchmark.png", dpi=170)
        if args.publish:
            fig.savefig(
                S.parents[1] / "docs/assets/images/simulation-benchmark.png", dpi=170
            )
        plt.close(fig)
    except ImportError:
        pass
    print(
        json.dumps(
            {
                "cases": len(cases),
                "passed": True,
                "wall_seconds": report["wall_seconds"],
                "worst_nonfault_depth_RMSE_m": max(
                    x["depth_RMSE_last2s_m"]
                    for x in cases
                    if x["scenario"] != "motor-fault"
                ),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
