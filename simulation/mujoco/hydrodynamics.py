"""Explicit water-relative passive drag and a tension-only lumped tether."""

import numpy as np

G = 9.80665


def current(k, time, position):
    w = k["water"]
    return (
        np.asarray(w["current_world_m_s"])
        + np.asarray(w["oscillation_world_m_s"])
        * np.sin(2 * np.pi * time / w["oscillation_period_s"])
        + np.asarray(w["shear_world_per_m"])
        * (position[2] - k["simulation"]["surface_z_m"])
    )


def drag(k, relative_velocity_body, omega_body):
    v = np.asarray(relative_velocity_body)
    w = np.asarray(omega_body)
    f = (
        -np.asarray(k["assumed_linear_drag"]) * v
        - np.asarray(k["assumed_quadratic_drag"]) * np.abs(v) * v
    )
    torque = (
        -np.asarray(k["assumed_angular_linear_drag"]) * w
        - np.asarray(k["assumed_angular_quadratic_drag"]) * np.abs(w) * w
    )
    return f, torque


def tether(k, point_world, velocity_world):
    t = k["tether"]
    if not t["enabled"]:
        return np.zeros(3)
    delta = np.asarray(point_world) - np.asarray(t["anchor_world_m"])
    length = np.linalg.norm(delta)
    if length <= t["rest_length_m"] or length < 1e-12:
        return np.zeros(3)
    direction = delta / length
    tension = max(
        0.0,
        t["stiffness_N_m"] * (length - t["rest_length_m"])
        + t["damping_N_s_m"] * np.dot(velocity_world, direction),
    )
    return -tension * direction
