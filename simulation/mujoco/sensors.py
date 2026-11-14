"""Seeded sample-and-hold measurements; no global pose or linear velocity sensor."""

from copy import deepcopy
import math
import numpy as np
import mujoco

try:
    from .hydrodynamics import G
except ImportError:
    from hydrodynamics import G


class SensorSuite:
    def __init__(self, k, seed):
        self.k = k
        self.seed = seed
        self.reset()

    def reset(self):
        self.rng = np.random.default_rng(np.random.SeedSequence(self.seed).spawn(2)[1])
        s = self.k["sensors"]
        self.bias = self.rng.normal(0, s["pressure_bias_std_Pa"])
        self.last_time = None
        self.last_depth = None
        self.rate = 0.0
        self.cached = None

    def sample(self, time, position, rotation, quaternion, gyro, specific_acceleration):
        s = self.k["sensors"]
        if (
            self.last_time is not None
            and time - self.last_time < 1 / s["rate_Hz"] - 1e-9
        ):
            return deepcopy(self.cached)
        depth = self.k["simulation"]["surface_z_m"] - position[2]
        pressure = (
            s["atmospheric_pressure_Pa"]
            + self.k["water_density_kg_m3"] * G * depth
            + self.bias
            + self.rng.normal(0, s["pressure_std_Pa"])
        )
        measured = (pressure - s["atmospheric_pressure_Pa"]) / (
            self.k["water_density_kg_m3"] * G
        )
        if self.last_time is not None:
            dt = time - self.last_time
            raw = (measured - self.last_depth) / dt
            self.rate += (raw - self.rate) * (
                -np.expm1(-dt / s["depth_rate_filter_tau_s"])
            )
        # Small-angle rotation noise is applied to a valid normalized quaternion.
        noise = self.rng.normal(0, s["attitude_std_rad"], 3)
        angle = np.linalg.norm(noise)
        dq = np.r_[
            np.cos(angle / 2),
            noise * (np.sin(angle / 2) / angle if angle > 1e-12 else 0.5),
        ]
        q = np.zeros(4)
        mujoco.mju_mulQuat(q, quaternion, dq)
        q /= np.linalg.norm(q)
        mat = np.zeros(9)
        mujoco.mju_quat2Mat(mat, q)
        mat = mat.reshape(3, 3)
        rpy = [
            math.atan2(mat[2, 1], mat[2, 2]),
            math.asin(np.clip(-mat[2, 0], -1, 1)),
            math.atan2(mat[1, 0], mat[0, 0]),
        ]
        self.cached = {
            "time_s": float(time),
            "pressure_Pa": float(pressure),
            "depth_m": float(measured),
            "depth_rate_m_s": float(self.rate),
            "attitude_quaternion_wxyz": q.tolist(),
            "attitude_rpy_rad": rpy,
            "gyro_body_rad_s": (
                np.asarray(gyro) + self.rng.normal(0, s["gyro_std_rad_s"], 3)
            ).tolist(),
            "specific_acceleration_body_m_s2": (
                np.asarray(specific_acceleration)
                + self.rng.normal(0, s["accelerometer_std_m_s2"], 3)
            ).tolist(),
            "attitude_source": "Noisy attitude proxy, not a validated IMU estimator",
        }
        self.last_time = float(time)
        self.last_depth = measured
        return deepcopy(self.cached)
