"""Reproducible scenario runner, keyboard control and sensor-based automatic demonstrations."""

import argparse
import csv
import json
import time
from pathlib import Path
from datetime import datetime, timezone

import mujoco
from environment import ROV, S
from manual_control import ManualControl


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--configuration", choices=["base", "with-buoyancy"], default="base"
    )
    parser.add_argument(
        "--scenario",
        choices=[
            "pool",
            "seawater",
            "cross-current",
            "tethered",
            "motor-fault",
            "native-fluid",
        ],
        default="pool",
    )
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--config",
        type=Path,
        help="JSON override object or calibration report containing overrides",
    )
    parser.add_argument("--feedback", choices=["sensors", "truth"], default="sensors")
    parser.add_argument(
        "--timestep",
        type=float,
        help="Physics timestep; control and sensor periods must align",
    )
    parser.add_argument("--viewer", action="store_true")
    parser.add_argument(
        "--manual", action="store_true", help="Keyboard setpoints; requires --viewer"
    )
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--seconds", type=float, default=16)
    args = parser.parse_args()
    if args.manual and not args.viewer:
        parser.error("--manual requires --viewer")
    if args.seconds <= 0:
        parser.error("--seconds must be positive")
    output = args.output_dir or S.parents[1] / "runs" / datetime.now(
        timezone.utc
    ).strftime("%Y%m%dT%H%M%S_%fZ")
    output.mkdir(parents=True, exist_ok=True)
    patch = json.loads(args.config.read_text()) if args.config else {}
    patch = patch.get("overrides", patch)
    if args.timestep is not None:
        patch.setdefault("simulation", {})["timestep_s"] = args.timestep
    env = ROV(
        configuration=args.configuration,
        scenario=args.scenario,
        seed=args.seed,
        overrides=patch,
    )
    dt = env.model.opt.timestep
    control_ticks = round(env.k["simulation"]["control_period_s"] / dt)
    render_ticks = max(1, round(0.1 / dt))
    manual = ManualControl() if args.manual else None
    rows, frames = [], []
    viewer = renderer = driving = None
    state = env.state()
    if manual:
        from desktop_viewer import DrivingWindow

        driving = DrivingWindow(env.model, env.data, manual)
    elif args.viewer:
        from mujoco import viewer as mjviewer

        viewer = mjviewer.launch_passive(
            env.model,
            env.data,
            key_callback=manual.key_callback if manual else None,
            show_left_ui=False,
            show_right_ui=False,
        )
        viewer.cam.distance = 0.65
        viewer.cam.elevation = -20
        viewer.cam.azimuth = 125
        viewer.opt.geomgroup[3] = 0
    if args.render:
        renderer = mujoco.Renderer(env.model, height=480, width=640)
        opt = mujoco.MjvOption()
        opt.geomgroup[3] = 0
    if manual:
        print(
            "MANUAL: W/S forward/reverse; A/D heading; U/J depth; X zero surge and hold current depth/heading.\n"
            "Hold W/S to move, release to zero surge. Losing focus also zeros surge. X does not hold horizontal position.",
            flush=True,
        )
    try:
        for i in range(int(args.seconds / dt)):
            if driving and i % control_ticks == 0 and not driving.poll():
                break
            if viewer and i % control_ticks == 0 and not viewer.is_running():
                break
            t = i * dt
            if manual:
                if manual.apply_pending(state):
                    print(manual.label(state), flush=True)
                depth, surge, yaw = manual.depth, manual.surge, manual.yaw
            else:
                depth = 1.2 if t < 3 else (0.9 if t < 7 else 1.2)
                surge = 0 if t < 5 else (2 if t < 10 else 0)
                yaw = 0 if t < 9 else 0.8
            if i % control_ticks == 0:
                command = env.controller(
                    depth,
                    surge,
                    yaw,
                    measurement=env.measurements()
                    if args.feedback == "sensors"
                    else None,
                )
            state = env.step(command)
            pos, rpy, velocity, omega = state
            if i % control_ticks == 0:
                sensed = env.measurements()
                diag = env.diagnostics
                rows.append(
                    [
                        float(env.data.time),
                        *pos,
                        *rpy,
                        *env.force,
                        depth,
                        yaw,
                        sensed["depth_m"],
                        sensed["pressure_Pa"],
                        *diag["current_world_m_s"],
                        diag["tether_tension_N"],
                        diag["allocation"].get("weighted_residual_norm", 0.0),
                    ]
                )
            if viewer and i % control_ticks == 0:
                with viewer.lock():
                    viewer.cam.lookat[:] = pos
                text = (
                    manual.label(state)
                    if manual
                    else "AUTO DEMO | Add --manual for keyboard control"
                )
                viewer.set_texts(
                    (
                        mujoco.mjtFontScale.mjFONTSCALE_100,
                        mujoco.mjtGridPos.mjGRID_TOPLEFT,
                        text,
                        "",
                    )
                )
                viewer.sync()
                time.sleep(dt * control_ticks)
            if driving and i % control_ticks == 0:
                driving.draw(state)
                time.sleep(dt * control_ticks)
            if renderer and i % render_ticks == 0:
                cam = mujoco.MjvCamera()
                cam.lookat[:] = pos
                cam.distance, cam.azimuth, cam.elevation = 0.6, 130, -24
                renderer.update_scene(env.data, cam, scene_option=opt)
                frames.append(renderer.render().copy())
        name = (
            "manual_states.csv"
            if manual
            else ("demo_states.csv" if args.render else "viewer_states.csv")
        )
        with (output / name).open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "time_s",
                    "x_m",
                    "y_m",
                    "z_m",
                    "roll_rad",
                    "pitch_rad",
                    "yaw_rad",
                    "H_LEFT_N",
                    "H_RIGHT_N",
                    "V_LEFT_N",
                    "V_RIGHT_N",
                    "target_depth_m",
                    "target_yaw_rad",
                    "measured_depth_m",
                    "pressure_Pa",
                    "current_x_m_s",
                    "current_y_m_s",
                    "current_z_m_s",
                    "tether_tension_N",
                    "allocation_weighted_residual",
                ]
            )
            writer.writerows(rows)
        if renderer and frames:
            from PIL import Image
            import imageio.v2 as imageio

            Image.fromarray(frames[-1]).save(output / "simulation.png")
            renderer.update_scene(env.data, "front_camera", scene_option=opt)
            Image.fromarray(renderer.render()).save(output / "front-camera.png")
            imageio.mimsave(output / "demo.mp4", frames, fps=10, macro_block_size=16)
        metadata = env.metadata()
        metadata.update(
            feedback=args.feedback,
            control_period_s=env.k["simulation"]["control_period_s"],
            simulated_seconds=float(env.data.time),
        )
        (output / "run_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
        print(
            json.dumps(
                {
                    "output_directory": str(output.resolve()),
                    "configuration": args.configuration,
                    "scenario": args.scenario,
                    "seed": args.seed,
                    "engine_version": mujoco.__version__,
                    "feedback": args.feedback,
                    "mode": "manual_setpoints" if manual else "automatic_demo",
                    "simulated_seconds": env.data.time,
                    "final_position_m": state[0].tolist(),
                    "final_rpy_rad": state[1].tolist(),
                    "mass_and_hydrodynamics": "assumed, not calibrated",
                },
                indent=2,
            )
        )
    finally:
        if driving:
            driving.close()
        if viewer:
            viewer.close()
        if renderer:
            renderer.close()


if __name__ == "__main__":
    main()
