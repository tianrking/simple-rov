"""Reproducible fully-submerged ROV plant; explicit SI conventions and calibration limits."""

from pathlib import Path
import hashlib, json, math, xml.etree.ElementTree as ET
import numpy as np
import mujoco

try:
    from .configuration import load
    from .actuators import Allocator, Thrusters
    from .hydrodynamics import current, drag, tether, G
    from .sensors import SensorSuite
except ImportError:
    from configuration import load
    from actuators import Allocator, Thrusters
    from hydrodynamics import current, drag, tether, G
    from sensors import SensorSuite
S = Path(__file__).resolve().parent


class SimulationBoundary(RuntimeError):
    pass


class ROV:
    """Force-command plant. state() is ground truth; measurements() is a sampled sensor proxy."""

    def __init__(self, configuration="base", scenario="pool", seed=0, overrides=None):
        if configuration not in ("base", "with-buoyancy"):
            raise ValueError("Unknown assembly configuration: " + configuration)
        self.configuration = configuration
        self.scenario = scenario
        self.seed = int(seed)
        self.k = load(scenario, overrides)
        self.map = json.loads((S / "ACTUATOR_MAP.json").read_text())
        path = S / (
            "simple_rov_with_buoyancy.xml"
            if configuration == "with-buoyancy"
            else "simple_rov.xml"
        )
        xml = ET.parse(path).getroot()
        xml.find("compiler").set("meshdir", str(S / "meshes"))
        xml.find("option").set("timestep", str(self.k["simulation"]["timestep_s"]))
        body = xml.find("worldbody/body[@name='rov']")
        inertial = body.find("inertial")
        for key, value in [
            ("mass", self.k["assumed_dry_mass_kg"]),
            ("pos", self.k["assumed_CG_m"]),
            ("diaginertia", self.k["assumed_inertia_kg_m2"]),
        ]:
            inertial.set(
                key,
                " ".join(map(str, value)) if isinstance(value, list) else str(value),
            )
        if self.k["water"]["backend"] == "native-ellipsoid":
            xml.find("option").set("density", str(self.k["water_density_kg_m3"]))
            xml.find("option").set(
                "viscosity", str(self.k["water"]["native_viscosity_Pa_s"])
            )
            ET.SubElement(
                body,
                "geom",
                name="hydrodynamic_ellipsoid",
                type="ellipsoid",
                size=" ".join(map(str, self.k["water"]["native_ellipsoid_semiaxes_m"])),
                pos=" ".join(map(str, self.k["assumed_CG_m"])),
                fluidshape="ellipsoid",
                fluidcoef=" ".join(
                    map(str, self.k["water"]["native_fluid_coefficients"])
                ),
                contype="0",
                conaffinity="0",
                group="5",
                density="0",
            )
        reactions = []
        for site in self.map["sites"]:
            direction = np.asarray(site["thrust_direction"])
            sign = np.sign(np.dot(site["reaction_m_per_N"], direction))
            reaction = sign * self.k["assumed_reaction_torque_per_newton_m"] * direction
            reactions.append(reaction)
            xml.find("actuator/motor[@name='" + site["name"] + "']").set(
                "gear", " ".join(map(str, np.r_[direction, reaction]))
            )
        self.model = mujoco.MjModel.from_xml_string(
            ET.tostring(xml, encoding="unicode")
        )
        self.data = mujoco.MjData(self.model)
        self.bid = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_BODY, "rov")
        cg = np.asarray(self.k["assumed_CG_m"])
        columns = []
        for site, reaction in zip(self.map["sites"], reactions):
            direction = np.asarray(site["thrust_direction"])
            moment = np.cross(np.asarray(site["position_m"]) - cg, direction) + reaction
            columns.append(np.r_[direction, moment])
        self.wrench_matrix = np.asarray(columns).T
        self.A = self.wrench_matrix[[0, 2, 3, 5]]
        effect = np.asarray(self.k["thrusters"]["effectiveness"])
        lo = np.where(effect == 0, 0, -self.k["assumed_reverse_limit_N"])
        hi = np.where(effect == 0, 0, self.k["forward_limit_N"])
        self.allocator = Allocator(
            self.A * effect, lo, hi, self.k["thrusters"]["allocation_weights"]
        )
        self.motors = Thrusters(self.k, self.model.opt.timestep)
        self.sensor_suite = SensorSuite(self.k, self.seed)
        configs = json.loads(
            (S.parents[1] / "mechanical/configurations.json").read_text()
        )
        bounds = configs[configuration]["bounds_mm"]
        self.envelope_corners = (
            np.array(
                [
                    [x, y, z]
                    for x in bounds[0:2]
                    for y in bounds[2:4]
                    for z in bounds[4:6]
                ]
            )
            / 1000
        )
        self.reset()

    @property
    def force(self):
        return self.motors.force

    def reset(self, roll=0, yaw=0, pitch=0, depth=1.2, position=None):
        if not np.isfinite([roll, yaw, pitch, depth]).all():
            raise ValueError("Reset pose must be finite")
        mujoco.mj_resetData(self.model, self.data)
        self.data.qpos[:3] = (
            [0, 0, self.k["simulation"]["surface_z_m"] - depth]
            if position is None
            else np.asarray(position, float)
        )
        if not np.isfinite(self.data.qpos[:3]).all():
            raise ValueError("Reset position must be finite")
        cr, sr = np.cos(roll / 2), np.sin(roll / 2)
        cp, sp = np.cos(pitch / 2), np.sin(pitch / 2)
        cy, sy = np.cos(yaw / 2), np.sin(yaw / 2)
        self.data.qpos[3:7] = [
            cr * cp * cy + sr * sp * sy,
            sr * cp * cy - cr * sp * sy,
            cr * sp * cy + sr * cp * sy,
            cr * cp * sy - sr * sp * cy,
        ]
        self.motors.reset()
        self.sensor_suite.reset()
        self._integral = 0.0
        self._controller_time = 0.0
        self._depth_target = None
        self.diagnostics = {}
        self.allocator.last = {}
        mujoco.mj_forward(self.model, self.data)
        self._check_boundary()
        self.measurements()
        return self.state()

    def state(self):
        R = self.data.xmat[self.bid].reshape(3, 3)
        jp = np.zeros((3, self.model.nv))
        jr = np.zeros_like(jp)
        mujoco.mj_jacBodyCom(self.model, self.data, jp, jr, self.bid)
        rpy = np.array(
            [
                math.atan2(R[2, 1], R[2, 2]),
                math.asin(np.clip(-R[2, 0], -1, 1)),
                math.atan2(R[1, 0], R[0, 0]),
            ]
        )
        return (
            self.data.xpos[self.bid].copy(),
            rpy,
            jp @ self.data.qvel,
            jr @ self.data.qvel,
        )

    def measurements(self):
        p, _, _, _ = self.state()
        return self.sensor_suite.sample(
            self.data.time,
            p,
            self.data.xmat[self.bid].reshape(3, 3),
            self.data.xquat[self.bid],
            self.data.sensor("gyro").data,
            self.data.sensor("accel").data,
        )

    def allocate(self, surge_N, heave_N, roll_Nm, yaw_Nm):
        return self.allocator.solve([surge_N, heave_N, roll_Nm, yaw_Nm])

    def controller(self, depth=1.2, surge_N=0, yaw=0, roll=0, measurement=None):
        if not np.isfinite([depth, surge_N, yaw, roll]).all():
            raise ValueError("Controller targets must be finite")
        p, rpy, v, w = self.state()
        R = self.data.xmat[self.bid].reshape(3, 3)
        wb = R.T @ w
        if measurement is not None:
            rpy = np.asarray(measurement["attitude_rpy_rad"])
            Rflat = np.zeros(9)
            mujoco.mju_quat2Mat(
                Rflat, np.asarray(measurement["attitude_quaternion_wxyz"])
            )
            R = Rflat.reshape(3, 3)
            z = self.k["simulation"]["surface_z_m"] - measurement["depth_m"]
            vz = -measurement["depth_rate_m_s"]
            wb = np.asarray(measurement["gyro_body_rad_s"])
        else:
            z = p[2]
            vz = v[2]
        c = self.k["controller"]
        dt = max(0, min(0.1, self.data.time - self._controller_time))
        self._controller_time = float(self.data.time)
        if self._depth_target is None or abs(self._depth_target - depth) > 0.01:
            self._integral = 0.0
        self._depth_target = depth
        error = self.k["simulation"]["surface_z_m"] - depth - z
        net = G * (
            self.k["water_density_kg_m3"] * self.k["assumed_displaced_volume_m3"]
            - self.k["assumed_dry_mass_kg"]
        )
        heave = (
            c["depth_kp_N_m"] * error
            - c["depth_kd_N_s_m"] * vz
            + c["depth_ki_N_per_m_s"] * self._integral
            - net
            - R[2, 0] * surge_N
        ) / max(0.3, R[2, 2])
        angle = math.atan2(math.sin(yaw - rpy[2]), math.cos(yaw - rpy[2]))
        command = self.allocate(
            surge_N,
            heave,
            c["roll_kp_Nm_rad"] * (roll - rpy[0]) - c["roll_kd_Nm_s_rad"] * wb[0],
            c["yaw_kp_Nm_rad"] * angle - c["yaw_kd_Nm_s_rad"] * wb[2],
        )
        if abs(self.allocator.last["residual"][1]) < 1e-5 and abs(rpy[0]) < 0.5:
            self._integral = float(
                np.clip(
                    self._integral + error * dt,
                    -c["integral_limit_m_s"],
                    c["integral_limit_m_s"],
                )
            )
        return command

    def step_normalized(self, commands):
        return self.step(self.motors.normalized_to_force(commands))

    def _check_boundary(self):
        R = self.data.xmat[self.bid].reshape(3, 3)
        top = np.max((self.envelope_corners @ R.T + self.data.xpos[self.bid])[:, 2])
        if (
            top
            > self.k["simulation"]["surface_z_m"]
            - self.k["simulation"]["surface_clearance_m"]
        ):
            raise SimulationBoundary(
                "Fully submerged envelope crossed the configured surface-clearance boundary"
            )

    def step(self, forces):
        d, m, k = self.data, self.model, self.k
        self._check_boundary()
        d.qfrc_applied[:] = 0
        d.ctrl[:] = self.motors.step(forces, float(d.time))
        R = d.xmat[self.bid].reshape(3, 3)
        p, _, v, w = self.state()
        cg = d.xipos[self.bid].copy()
        water = current(k, d.time, p)
        point = p + R @ np.asarray(k["water"]["drag_center_body_m"])
        vp = v + np.cross(w, point - cg)
        relative = R.T @ (vp - water)
        omega = R.T @ w
        if k["water"]["backend"] == "analytic":
            f, tau = drag(k, relative, omega)
            mujoco.mj_applyFT(m, d, R @ f, R @ tau, point, self.bid, d.qfrc_applied)
            drag_power = float(f @ relative + tau @ omega)
        else:
            m.opt.wind[:] = water
            drag_power = None
        buoyancy = k["water_density_kg_m3"] * G * k["assumed_displaced_volume_m3"]
        cb = p + R @ np.asarray(k["assumed_CB_m"])
        mujoco.mj_applyFT(
            m,
            d,
            np.array([0.0, 0.0, buoyancy]),
            np.zeros(3),
            cb,
            self.bid,
            d.qfrc_applied,
        )
        attachment = p + R @ np.asarray(k["tether"]["attachment_body_m"])
        vt = v + np.cross(w, attachment - cg)
        line_force = tether(k, attachment, vt)
        mujoco.mj_applyFT(
            m, d, line_force, np.zeros(3), attachment, self.bid, d.qfrc_applied
        )
        self.diagnostics = {
            "current_world_m_s": water.tolist(),
            "relative_velocity_body_m_s": relative.tolist(),
            "analytic_drag_power_W": drag_power,
            "tether_force_world_N": line_force.tolist(),
            "tether_tension_N": float(np.linalg.norm(line_force)),
            "thrust_wrench_about_CG": (self.wrench_matrix @ self.force).tolist(),
            "command_timed_out": self.motors.timed_out,
            "allocation": self.allocator.last.copy(),
        }
        mujoco.mj_step(m, d)
        if not np.isfinite(d.qpos).all() or not np.isfinite(d.qvel).all():
            raise RuntimeError("Nonfinite simulation state")
        # mj_step leaves derived body transforms at the previous kinematic evaluation.
        # Refresh once so returned truth, sensor data and rendering refer to the new time.
        mujoco.mj_forward(m, d)
        self._check_boundary()
        if d.time - self.sensor_suite.last_time >= 1 / k["sensors"]["rate_Hz"] - 1e-9:
            self.measurements()
        return self.state()

    def metadata(self):
        names = [
            "environment.py",
            "configuration.py",
            "hydrodynamics.py",
            "actuators.py",
            "sensors.py",
            "config.json",
            "scenarios.json",
            "simple_rov.xml",
            "simple_rov_with_buoyancy.xml",
            "ACTUATOR_MAP.json",
        ]
        return {
            "engine": "MuJoCo",
            "engine_version": mujoco.__version__,
            "numpy_version": np.__version__,
            "seed": self.seed,
            "scenario": self.scenario,
            "assembly": self.configuration,
            "resolved_config": self.k,
            "runtime_wrench_matrix_about_CG": self.wrench_matrix.tolist(),
            "controlled_allocation_rank": int(np.linalg.matrix_rank(self.allocator.A)),
            "source_sha256": {
                n: hashlib.sha256((S / n).read_bytes()).hexdigest() for n in names
            },
            "physical_calibration": False,
            "scope": "Fully submerged rigid-body approximation. No CFD, free surface, distributed tether or validated IMU estimator. Analytic backend omits added mass; native ellipsoid is an uncalibrated comparative approximation.",
        }
