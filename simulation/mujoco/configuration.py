"""Validated, per-instance configuration and seeded uncertainty draws."""

from copy import deepcopy
from pathlib import Path
import json
import numpy as np

S = Path(__file__).resolve().parent


def merge(base, patch):
    if not isinstance(patch, dict):
        raise ValueError("Configuration patches must be objects")
    out = deepcopy(base)
    for key, value in patch.items():
        if key not in out:
            raise ValueError("Unknown configuration key: " + key)
        out[key] = (
            merge(out[key], value) if isinstance(out[key], dict) else deepcopy(value)
        )
    return out


def vector(value, n, name, minimum=None):
    a = np.asarray(value, dtype=float)
    if a.shape != (n,) or not np.isfinite(a).all():
        raise ValueError(name + " must be a finite " + str(n) + "-vector")
    if minimum is not None and np.any(a < minimum):
        raise ValueError(name + " below allowed minimum")
    return a


def positive(value, name, zero=False):
    if not np.isfinite(value) or value < 0 or (value == 0 and not zero):
        raise ValueError(name + " must be " + ("nonnegative" if zero else "positive"))


def validate(k):
    for value in [
        k["fully_submerged_only"],
        k["tether"]["enabled"],
        k["randomization"]["enabled"],
    ]:
        if not isinstance(value, bool):
            raise ValueError("Enabled/full-immersion flags must be Boolean")
    positive(k["assumed_reaction_torque_per_newton_m"], "reaction torque", True)
    for key in [
        "water_density_kg_m3",
        "assumed_dry_mass_kg",
        "assumed_displaced_volume_m3",
        "assumed_motor_time_constant_s",
        "forward_limit_N",
        "assumed_reverse_limit_N",
    ]:
        positive(k[key], key)
    inertia = vector(k["assumed_inertia_kg_m2"], 3, "inertia", 1e-12)
    if np.any(2 * inertia > inertia.sum() + 1e-12):
        raise ValueError("Inertia violates triangle inequalities")
    for key in ["assumed_CG_m", "assumed_CB_m"]:
        vector(k[key], 3, key)
    for key in [
        "assumed_linear_drag",
        "assumed_quadratic_drag",
        "assumed_angular_linear_drag",
        "assumed_angular_quadratic_drag",
    ]:
        vector(k[key], 3, key, 0)
    sim = k["simulation"]
    positive(sim["timestep_s"], "timestep")
    positive(sim["control_period_s"], "control period")
    ratio = sim["control_period_s"] / sim["timestep_s"]
    if sim["timestep_s"] > 0.01 or abs(ratio - round(ratio)) > 1e-8:
        raise ValueError(
            "Control period must be an integer multiple of physics timestep <= 0.01 s"
        )
    positive(sim["surface_clearance_m"], "surface clearance", True)
    w = k["water"]
    if w["backend"] not in ("analytic", "native-ellipsoid"):
        raise ValueError("Unknown water backend")
    for key in [
        "current_world_m_s",
        "oscillation_world_m_s",
        "shear_world_per_m",
        "drag_center_body_m",
    ]:
        vector(w[key], 3, key)
    positive(w["oscillation_period_s"], "current period")
    positive(w["native_viscosity_Pa_s"], "viscosity", True)
    vector(w["native_ellipsoid_semiaxes_m"], 3, "ellipsoid", 1e-9)
    vector(w["native_fluid_coefficients"], 5, "fluid coefficients", 0)
    t = k["thrusters"]
    effect = vector(t["effectiveness"], 4, "effectiveness", 0)
    if np.any(effect > 1):
        raise ValueError("Effectiveness must lie in [0,1]")
    vector(t["allocation_weights"], 4, "allocation weights", 1e-12)
    for key in ["command_delay_s", "slew_rate_N_s", "deadband_N", "timeout_s"]:
        positive(t[key], key, key in ("command_delay_s", "deadband_N"))
    curve = t["command_curve"]
    x = np.asarray(curve["input"], float)
    y = np.asarray(curve["force_N"], float)
    if (
        x.ndim != 1
        or len(x) < 3
        or y.shape != x.shape
        or not np.isfinite(x).all()
        or not np.isfinite(y).all()
        or np.any(np.diff(x) <= 0)
        or np.any(np.diff(y) < 0)
        or x[0] != -1
        or x[-1] != 1
        or 0 not in x
        or y[list(x).index(0)] != 0
    ):
        raise ValueError(
            "Command curve must be finite monotone, cover [-1,1] and pass through zero"
        )
    if y[0] < -k["assumed_reverse_limit_N"] or y[-1] > k["forward_limit_N"]:
        raise ValueError("Curve exceeds force limits")
    sen = k["sensors"]
    positive(sen["rate_Hz"], "sensor rate")
    positive(sen["depth_rate_filter_tau_s"], "sensor filter")
    if sen["rate_Hz"] > 1 / sim["timestep_s"]:
        raise ValueError("Sensor rate exceeds physics rate")
    if (
        abs(
            1 / sen["rate_Hz"] / sim["timestep_s"]
            - round(1 / sen["rate_Hz"] / sim["timestep_s"])
        )
        > 1e-8
    ):
        raise ValueError("Sensor period must align to physics ticks")
    for key in [
        "pressure_std_Pa",
        "pressure_bias_std_Pa",
        "attitude_std_rad",
        "gyro_std_rad_s",
        "accelerometer_std_m_s2",
    ]:
        positive(sen[key], key, True)
    positive(sen["atmospheric_pressure_Pa"], "atmospheric pressure")
    for key, value in k["controller"].items():
        positive(value, key, True)
    tether = k["tether"]
    vector(tether["anchor_world_m"], 3, "anchor")
    vector(tether["attachment_body_m"], 3, "attachment")
    for key in ["rest_length_m", "stiffness_N_m", "damping_N_s_m"]:
        positive(tether[key], key, True)
    for key, value in k["randomization"].items():
        if key != "enabled" and (not np.isfinite(value) or value < 0 or value >= 1):
            raise ValueError("Randomization fractions must be in [0,1)")
    if not k["fully_submerged_only"]:
        raise ValueError("This model requires full immersion")


def load(scenario="pool", overrides=None, seed=0):
    scenarios = json.loads((S / "scenarios.json").read_text())
    if scenario not in scenarios:
        raise ValueError("Unknown scenario: " + scenario)
    k = merge(
        json.loads((S / "config.json").read_text()), scenarios[scenario]["overrides"]
    )
    if overrides:
        k = merge(k, overrides)
    validate(k)
    rng = np.random.default_rng(np.random.SeedSequence(seed).spawn(2)[0])
    r = k["randomization"]
    if r["enabled"]:
        for key, fraction in [
            ("assumed_dry_mass_kg", "mass_fraction"),
            ("assumed_displaced_volume_m3", "volume_fraction"),
            ("assumed_motor_time_constant_s", "motor_lag_fraction"),
        ]:
            k[key] *= rng.uniform(1 - r[fraction], 1 + r[fraction])
        for key in [
            "assumed_linear_drag",
            "assumed_quadratic_drag",
            "assumed_angular_linear_drag",
            "assumed_angular_quadratic_drag",
        ]:
            k[key] = (
                np.asarray(k[key])
                * rng.uniform(1 - r["drag_fraction"], 1 + r["drag_fraction"], 3)
            ).tolist()
        k["thrusters"]["effectiveness"] = (
            np.asarray(k["thrusters"]["effectiveness"])
            * rng.uniform(1 - r["thrust_fraction"], 1, 4)
        ).tolist()
    validate(k)
    return k
