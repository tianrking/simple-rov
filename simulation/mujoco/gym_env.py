"""Seedable sensor-based depth/heading task. No trained policy is included."""

import numpy as np
import gymnasium as gym
from gymnasium import spaces

try:
    from .environment import ROV, SimulationBoundary
except ImportError:
    from environment import ROV, SimulationBoundary


class SimpleROVEnv(gym.Env):
    metadata = {"render_modes": ["rgb_array"], "render_fps": 50}

    def __init__(
        self,
        scenario="pool",
        configuration="base",
        duration_s=20.0,
        randomize=False,
        render_mode=None,
    ):
        if duration_s <= 0 or not np.isfinite(duration_s):
            raise ValueError("Duration must be positive")
        if render_mode not in (None, "rgb_array"):
            raise ValueError("Supported render_mode: rgb_array")
        self.scenario = scenario
        self.configuration = configuration
        self.duration = duration_s
        self.randomize = randomize
        self.render_mode = render_mode
        self.renderer = None
        self.rov = None
        self.action_space = spaces.Box(-1, 1, (4,), np.float32)
        self.observation_space = spaces.Box(-1, 1, (13,), np.float32)
        self.observation_scales = np.asarray(
            [2, 1, 1, np.pi, np.pi, 2, 4, 4, 4, 1, 1, 1, 1], np.float32
        )

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.close()
        physical_seed = int(self.np_random.integers(0, 2**31 - 1))
        self.rov = ROV(
            self.configuration,
            self.scenario,
            seed=physical_seed,
            overrides={"randomization": {"enabled": self.randomize}},
        )
        self.goal_depth = float(self.np_random.uniform(0.8, 1.5))
        self.goal_yaw = float(self.np_random.uniform(-0.6, 0.6))
        self.rov.reset(
            depth=self.goal_depth + float(self.np_random.uniform(-0.12, 0.12)),
            roll=float(self.np_random.uniform(-0.12, 0.12)),
            yaw=self.goal_yaw + float(self.np_random.uniform(-0.2, 0.2)),
        )
        self.previous = np.zeros(4)
        self.steps = 0
        self.substeps = round(
            self.rov.k["simulation"]["control_period_s"] / self.rov.model.opt.timestep
        )
        self.max_steps = max(
            1,
            int(np.ceil(self.duration / self.rov.k["simulation"]["control_period_s"])),
        )
        return self._observation(), self._info("reset")

    def _observation(self):
        s = self.rov.measurements()
        roll, pitch, yaw = s["attitude_rpy_rad"]
        error = self.goal_yaw - yaw
        raw = np.asarray(
            [
                self.goal_depth - s["depth_m"],
                np.sin(error),
                np.cos(error),
                roll,
                pitch,
                s["depth_rate_m_s"],
                *s["gyro_body_rad_s"],
                *self.previous,
            ],
            dtype=np.float32,
        )
        return np.clip(raw / self.observation_scales, -1, 1)

    def _info(self, reason):
        p, r, _, _ = self.rov.state()
        return {
            "time_s": float(self.rov.data.time),
            "reason": reason,
            "goal_depth_m": self.goal_depth,
            "goal_yaw_rad": self.goal_yaw,
            "ground_truth_depth_m": float(-p[2]),
            "ground_truth_rpy_rad": r.copy(),
            "ground_truth_is_diagnostic_only": True,
            "physical_calibrated": False,
        }

    def step(self, action):
        if self.rov is None:
            raise RuntimeError("Call reset before step")
        action = np.asarray(action, dtype=np.float32)
        if not self.action_space.contains(action):
            raise ValueError("Action must be finite shape (4,) within [-1,1]")
        terminated = False
        reason = "running"
        for _ in range(self.substeps):
            try:
                self.rov.step_normalized(action)
            except SimulationBoundary:
                terminated = True
                reason = "surface_boundary"
                break
            _, r, _, _ = self.rov.state()
            if np.max(np.abs(r[:2])) > 1.0:
                terminated = True
                reason = "attitude_envelope"
                break
            if self.rov.data.ncon:
                terminated = True
                reason = "collision"
                break
        delta = action - self.previous
        self.previous = action.copy()
        self.steps += 1
        obs = self._observation()
        sensed = self.rov.measurements()
        roll, pitch, yaw = sensed["attitude_rpy_rad"]
        yaw_cost = 1 - np.cos(self.goal_yaw - yaw)
        cost = (
            4 * (self.goal_depth - sensed["depth_m"]) ** 2
            + 2 * yaw_cost
            + 0.5 * (roll**2 + pitch**2)
            + 0.02 * float(action @ action)
            + 0.05 * float(delta @ delta)
        )
        reward = -float(cost * self.rov.k["simulation"]["control_period_s"]) - (
            5.0 if terminated else 0.0
        )
        truncated = self.steps >= self.max_steps
        if truncated and not terminated:
            reason = "time_limit"
        return obs, reward, terminated, truncated, self._info(reason)

    def render(self):
        if self.rov is None:
            raise RuntimeError("Call reset before render")
        if self.render_mode is None:
            return None
        import mujoco

        if self.renderer is None:
            self.renderer = mujoco.Renderer(self.rov.model, height=480, width=640)
        cam = mujoco.MjvCamera()
        cam.lookat[:] = self.rov.data.xpos[self.rov.bid]
        cam.distance = 0.6
        cam.elevation = -24
        cam.azimuth = 130
        opt = mujoco.MjvOption()
        opt.geomgroup[3:] = 0
        self.renderer.update_scene(self.rov.data, cam, scene_option=opt)
        return self.renderer.render().copy()

    def close(self):
        if self.renderer is not None:
            self.renderer.close()
            self.renderer = None
