"""Bounded wrench allocation and delayed, rate-limited force response."""

from collections import deque
from itertools import product
import numpy as np


class Allocator:
    def __init__(self, matrix, lower, upper, weights):
        self.A = np.asarray(matrix, float)
        self.lower = np.asarray(lower, float)
        self.upper = np.asarray(upper, float)
        self.weights = np.asarray(weights, float)
        self.B = self.weights[:, None] * self.A
        # Every face of the four-dimensional box is considered when an unconstrained solution is infeasible.
        self.faces = []
        for status in product((-1, 0, 1), repeat=4):
            fixed = np.flatnonzero(status)
            free = np.flatnonzero(np.asarray(status) == 0)
            u = np.zeros(4)
            for i in fixed:
                u[i] = self.lower[i] if status[i] == -1 else self.upper[i]
            self.faces.append(
                (fixed, free, u, np.linalg.pinv(self.B[:, free]) if len(free) else None)
            )
        self.pinv = np.linalg.pinv(self.B)
        self.last = {}

    def solve(self, wrench):
        b = self.weights * np.asarray(wrench, float)
        if b.shape != (4,) or not np.isfinite(b).all():
            raise ValueError("Wrench must be a finite 4-vector")
        trial = self.pinv @ b
        if np.all(trial >= self.lower - 1e-10) and np.all(trial <= self.upper + 1e-10):
            best = np.clip(trial, self.lower, self.upper)
        else:
            cost = float("inf")
            best = None
            for fixed, free, u0, pinv in self.faces:
                u = u0.copy()
                if len(free):
                    u[free] = pinv @ (b - self.B[:, fixed] @ u[fixed])
                if np.any(u < self.lower - 1e-9) or np.any(u > self.upper + 1e-9):
                    continue
                error = self.B @ u - b
                value = float(error @ error)
                if value < cost:
                    cost = value
                    best = u
            if best is None:
                raise RuntimeError("No feasible actuator allocation")
            best = np.clip(best, self.lower, self.upper)
        residual = self.A @ best - np.asarray(wrench)
        self.last = {
            "requested_wrench": list(map(float, wrench)),
            "achieved_wrench": (self.A @ best).tolist(),
            "residual": residual.tolist(),
            "weighted_residual_norm": float(np.linalg.norm(self.weights * residual)),
            "rank": int(np.linalg.matrix_rank(self.A)),
            "saturated": bool(
                np.any(
                    np.isclose(best, self.lower, atol=1e-8)
                    | np.isclose(best, self.upper, atol=1e-8)
                )
            ),
        }
        return best


class Thrusters:
    def __init__(self, k, dt):
        self.k = k
        self.dt = dt
        self.lower = -k["assumed_reverse_limit_N"]
        self.upper = k["forward_limit_N"]
        self.t = k["thrusters"]
        self.delay_ticks = int(np.ceil(self.t["command_delay_s"] / dt - 1e-12))
        self.reset()

    def reset(self):
        self.force = np.zeros(4)
        self.queue = deque([np.zeros(4) for _ in range(self.delay_ticks)])
        self.target = np.zeros(4)
        self.last_command_time = 0.0
        self.timed_out = False

    def normalized_to_force(self, command):
        u = np.asarray(command, float)
        if u.shape != (4,) or not np.isfinite(u).all() or np.any(np.abs(u) > 1):
            raise ValueError("Normalized commands must be a finite 4-vector in [-1,1]")
        curve = self.t["command_curve"]
        return np.interp(u, curve["input"], curve["force_N"])

    def step(self, command, time):
        if command is not None:
            cmd = np.asarray(command, float)
            if cmd.shape != (4,) or not np.isfinite(cmd).all():
                raise ValueError("Thruster command must be a finite 4-vector")
            self.target = np.clip(cmd, self.lower, self.upper)
            self.last_command_time = time
        self.timed_out = time - self.last_command_time > self.t["timeout_s"]
        target = np.zeros(4) if self.timed_out else self.target.copy()
        target[np.abs(target) < self.t["deadband_N"]] = 0
        if self.timed_out:
            self.queue = deque([np.zeros(4) for _ in range(self.delay_ticks)])
        self.queue.append(target)
        delayed = self.queue.popleft()
        desired = delayed * np.asarray(self.t["effectiveness"])
        delta = (desired - self.force) * (
            -np.expm1(-self.dt / self.k["assumed_motor_time_constant_s"])
        )
        self.force += np.clip(
            delta, -self.t["slew_rate_N_s"] * self.dt, self.t["slew_rate_N_s"] * self.dt
        )
        # A zero-effectiveness actuator is a disabled output, not a slow coasting propeller model.
        self.force[np.asarray(self.t["effectiveness"]) == 0] = 0
        return self.force.copy()
