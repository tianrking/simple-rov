"""Behavioral and physical-invariant tests beyond the visual demonstration."""

from pathlib import Path
import hashlib, json, math
import numpy as np
from environment import ROV, SimulationBoundary, S
from hydrodynamics import drag, tether
from configuration import load


def rejects(fn):
    try:
        fn()
    except (ValueError, SimulationBoundary):
        return
    raise AssertionError("Expected invalid input to be rejected")


results = {}
rng = np.random.default_rng(42)
k = load()
rejects(lambda: load(overrides={"typo": 1}))
rejects(lambda: load(overrides={"assumed_dry_mass_kg": -1}))
rejects(lambda: load(overrides={"simulation": {"timestep_s": 0.003}}))
rejects(lambda: load(overrides={"thrusters": {"effectiveness": [1, 1, 2, 1]}}))
results["invalid_configs_rejected"] = True
for _ in range(100):
    v = rng.normal(size=3)
    w = rng.normal(size=3)
    f, t = drag(k, v, w)
    assert f @ v + t @ w <= 1e-12
results["drag_passivity_100_samples"] = True
kt = load("tethered")
anchor = np.asarray(kt["tether"]["anchor_world_m"])
assert np.all(tether(kt, anchor, np.zeros(3)) == 0)
f = tether(kt, anchor + [2, 0, 0], [1, 0, 0])
assert f[0] < 0 and np.linalg.norm(f[1:]) == 0
assert np.all(tether(kt, anchor + [2, 0, 0], [-100, 0, 0]) == 0)
results["tether_slack_tension_no_compression"] = True
e = ROV()
request = np.array([80, 90, 3, -2])
u = e.allocate(*request)
grad = e.allocator.B.T @ (e.allocator.B @ u - e.allocator.weights * request)
for i in range(4):
    if abs(u[i] - e.allocator.lower[i]) < 1e-7:
        assert grad[i] >= -1e-6
    elif abs(u[i] - e.allocator.upper[i]) < 1e-7:
        assert grad[i] <= 1e-6
    else:
        assert abs(grad[i]) < 1e-6
naive = np.clip(np.linalg.solve(e.A, request), e.allocator.lower, e.allocator.upper)
assert (
    np.linalg.norm(e.allocator.weights * (e.A @ u - request))
    <= np.linalg.norm(e.allocator.weights * (e.A @ naive - request)) + 1e-8
)
results["bounded_allocation_KKT_and_no_worse_than_clipping"] = True
fault = ROV(scenario="motor-fault")
u = fault.allocate(2, 0, 0, 0.2)
assert (
    u[0] == 0
    and fault.allocator.last["rank"] == 3
    and fault.allocator.last["weighted_residual_norm"] > 0
)
for _ in range(20):
    fault.step(u)
assert fault.force[0] == 0
results["failed_thruster_rank_loss_and_residual_visible"] = True
rejects(lambda: e.step([1, 2, float("nan"), 0]))
rejects(lambda: e.step_normalized([2, 0, 0, 0]))
rejects(lambda: e.reset(depth=0.05))
e.reset()
for _ in range(200):
    e.step([2, 2, 0, 0])
for _ in range(1000):
    e.step(None)
assert e.diagnostics["command_timed_out"] and np.max(np.abs(e.force)) < 0.002
results["watchdog_zeroes_stale_commands"] = True
# No force can appear before the configured transport delay.
e.reset()
e.step([1, 1, 1, 1])
assert np.all(e.force == 0)
for _ in range(9):
    e.step([1, 1, 1, 1])
assert np.all(e.force == 0)
e.step([1, 1, 1, 1])
assert np.all(e.force > 0)
results["transport_delay_ticks"] = e.motors.delay_ticks
# Sample-and-hold means repeated reads at the same time do not consume RNG.
e.reset()
a = e.measurements()
b = e.measurements()
assert a == b
for _ in range(3):
    e.step([0, 0, 0, 0])
assert e.measurements() == a
for _ in range(7):
    e.step([0, 0, 0, 0])
assert e.measurements()["time_s"] > a["time_s"]
results["sensor_sample_hold"] = True
sequences = []
for _ in range(2):
    e = ROV(seed=7, overrides={"randomization": {"enabled": True}})
    trace = []
    for tick in range(200):
        if tick % 10 == 0:
            command = e.controller(measurement=e.measurements())
        e.step(command)
        if tick % 10 == 0:
            trace.append([*e.data.qpos, *e.measurements()["gyro_body_rad_s"]])
    sequences.append(np.array(trace))
assert np.array_equal(*sequences)
results["same_seed_config_actions_exact_local_replay"] = True
assert load(seed=7, overrides={"randomization": {"enabled": True}}) != load(
    seed=8, overrides={"randomization": {"enabled": True}}
)
results["different_seed_changes_uncertainty"] = True
# A stationary vehicle sees current and moves with the flow. Co-moving velocity removes analytic drag.
e = ROV(scenario="cross-current")
e.step([0, 0, 0, 0])
assert e.diagnostics["relative_velocity_body_m_s"][0] < 0
native = ROV(scenario="native-fluid")
assert (
    native.model.opt.density == 997
    and np.count_nonzero(native.model.geom_fluid[:, 0]) == 1
)
for i in range(500):
    native.step(native.controller())
assert np.isfinite(native.data.qpos).all()
results["native_ellipsoid_one_fluid_geom_and_finite"] = True
# Changing mass and CG affects both physics and allocation, not just metadata.
e = ROV(overrides={"assumed_dry_mass_kg": 1.7, "assumed_CG_m": [0.01, 0, 0.006]})
assert abs(e.model.body_mass[e.bid] - 1.7) < 1e-12
assert abs(e.wrench_matrix[4, 0] - ROV().wrench_matrix[4, 0]) > 1e-5
results["runtime_mass_CG_applied_to_dynamics_and_allocation"] = True
no_reaction = ROV(overrides={"assumed_reaction_torque_per_newton_m": 0.0})
assert np.all(no_reaction.wrench_matrix[3, :2] == 0)
results["runtime_reaction_torque_applied"] = True
still = ROV(overrides={"water": {"current_world_m_s": [0.1, 0, 0]}})
still.data.qvel[0] = 0.1
__import__("mujoco").mj_forward(still.model, still.data)
still.step([0, 0, 0, 0])
assert np.linalg.norm(still.diagnostics["relative_velocity_body_m_s"]) < 1e-12
results["co_moving_water_has_zero_analytic_drag"] = True
# The calibration utility must recover known passive coefficients and reject unexcited data.
from calibrate import fit_drag
import tempfile, csv

with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / "synthetic.csv"
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "velocity_x_m_s",
                "velocity_y_m_s",
                "velocity_z_m_s",
                "drag_x_N",
                "drag_y_N",
                "drag_z_N",
            ]
        )
        for speed in [-0.5, -0.3, -0.1, 0.1, 0.3, 0.5]:
            writer.writerow(
                [speed] * 3
                + [
                    -3 * speed - 18 * abs(speed) * speed,
                    -4 * speed - 22 * abs(speed) * speed,
                    -5 * speed - 26 * abs(speed) * speed,
                ]
            )
    fitted = fit_drag(path)["overrides"]
    assert np.allclose(fitted["assumed_linear_drag"], [3, 4, 5]) and np.allclose(
        fitted["assumed_quadratic_drag"], [18, 22, 26]
    )
results["synthetic_drag_calibration_recovers_coefficients"] = True
quiet = ROV(
    overrides={"sensors": {"pressure_std_Pa": 0.0, "pressure_bias_std_Pa": 0.0}}
)
assert abs(quiet.measurements()["depth_m"] - 1.2) < 1e-12
results["pressure_to_depth_SI_conversion"] = True
limited = ROV()
for _ in range(100):
    limited.step(limited.controller(depth=100.0))
assert limited._integral == 0.0 and limited.allocator.last["saturated"]
results["saturated_depth_integral_does_not_wind_up"] = True
# Same 50 Hz control task at 1, 2 and 4 ms physics ticks.
final = []
for dt in [0.001, 0.002, 0.004]:
    e = ROV(overrides={"simulation": {"timestep_s": dt}})
    e.reset(roll=0.1)
    n = round(0.02 / dt)
    for i in range(round(3 / dt)):
        if i % n == 0:
            command = e.controller(depth=1.0, yaw=0.3)
        e.step(command)
    final.append(np.r_[e.state()[0], e.state()[1]])
difference = np.abs(np.asarray(final) - final[0])
position_spread = float(difference[:, :3].max())
attitude_spread = float(difference[:, 3:].max())
assert position_spread < 0.015 and attitude_spread < 0.015
results["timestep_convergence"] = {
    "timesteps_s": [0.001, 0.002, 0.004],
    "control_period_s": 0.02,
    "max_position_spread_m": position_spread,
    "max_attitude_spread_rad": attitude_spread,
}
names = [
    "environment.py",
    "configuration.py",
    "actuators.py",
    "hydrodynamics.py",
    "sensors.py",
    "config.json",
    "scenarios.json",
    "verify_foundation.py",
    "calibrate.py",
]
results.update(
    engine_version=__import__("mujoco").__version__,
    source_sha256={n: hashlib.sha256((S / n).read_bytes()).hexdigest() for n in names},
    passed=True,
    scope="Software invariants and uncalibrated model checks, not experimental validation.",
)
(S / "FOUNDATION_CHECKS.json").write_text(json.dumps(results, indent=2) + "\n")
print(json.dumps(results, indent=2))
