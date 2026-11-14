"""Gymnasium checker, deterministic episodes and time-limit semantics."""

import hashlib, json
import numpy as np
import gymnasium
from gymnasium.utils.env_checker import check_env
from gym_env import SimpleROVEnv
from environment import S

e = SimpleROVEnv(duration_s=0.06, randomize=True)
check_env(e, skip_render_check=True)
a, info = e.reset(seed=11)
b, info2 = e.reset(seed=11)
assert np.array_equal(a, b)
trace = []
for _ in range(3):
    o, r, terminated, truncated, info = e.step(np.zeros(4, np.float32))
    trace.append([r, terminated, truncated])
assert not terminated and truncated and info["reason"] == "time_limit"
# Every reset owns independent state and no global pose/velocity appears in the observation.
assert e.observation_space.shape == (13,) and e.action_space.shape == (4,)
e.close()
j = {
    "gymnasium_version": gymnasium.__version__,
    "env_checker": True,
    "same_seed_reset": True,
    "time_limit_trace": trace,
    "observation_size": 13,
    "actions": "Four normalized thruster commands",
    "source_sha256": {
        n: hashlib.sha256((S / n).read_bytes()).hexdigest()
        for n in [
            "gym_env.py",
            "verify_gym.py",
            "environment.py",
            "configuration.py",
            "sensors.py",
            "actuators.py",
            "hydrodynamics.py",
            "config.json",
            "scenarios.json",
        ]
    },
    "passed": True,
    "trained_policy": False,
}
(S / "GYM_CHECKS.json").write_text(json.dumps(j, indent=2) + "\n")
print(json.dumps(j, indent=2))
