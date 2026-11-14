"""Render traceable MuJoCo scenario videos, telemetry, a front camera and README preview."""

from pathlib import Path
import argparse, csv, hashlib, json, subprocess, sys, xml.etree.ElementTree as ET
import imageio.v2 as imageio
import imageio_ffmpeg
import mujoco
import numpy as np
from PIL import Image, ImageDraw, ImageFont

R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / "simulation/mujoco"))
from environment import ROV, S

CASES = [
    ("pool", "01  /  BASIC MOTION", "Depth changes, forward motion and heading hold"),
    (
        "cross-current",
        "02  /  CROSS-CURRENT",
        "World-frame water flow; lateral position is not controlled",
    ),
    (
        "tethered",
        "03  /  TETHER LOAD",
        "Tension-only line at the chassis eye; slack line cannot push",
    ),
    (
        "motor-fault",
        "04  /  ACTUATOR FAILURE",
        "H_LEFT disabled; allocation rank drops from four to three",
    ),
]
BG = "#102d38"
MUTED = "#9cbbc5"
WHITE = "#edf6f8"
ORANGE = "#ffad42"
TEAL = "#6ed6df"


def font(size):
    return ImageFont.load_default(size=size)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def display_model():
    xml = ET.parse(S / "simple_rov.xml").getroot()
    xml.find("compiler").set("meshdir", str(S / "meshes"))
    ET.SubElement(
        xml.find("asset"),
        "texture",
        type="skybox",
        builtin="gradient",
        rgb1=".035 .13 .20",
        rgb2=".12 .30 .39",
        width="256",
        height="1536",
    )
    head = xml.find("visual/headlight")
    head.set("ambient", ".55 .55 .55")
    head.set("diffuse", ".7 .7 .7")
    model = mujoco.MjModel.from_xml_string(ET.tostring(xml, encoding="unicode"))
    gid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, "BUY_TUBE")
    model.geom_rgba[gid] = [0.38, 0.56, 0.61, 1]
    return model


def connector(scene, kind, width, start, end, color):
    if np.linalg.norm(np.asarray(end) - start) < 1e-9:
        return
    geom = scene.geoms[scene.ngeom]
    mujoco.mjv_initGeom(
        geom,
        kind,
        np.zeros(3),
        np.zeros(3),
        np.eye(3).ravel(),
        np.array(color, np.float32),
    )
    mujoco.mjv_connector(
        geom, kind, width, np.asarray(start, float), np.asarray(end, float)
    )
    scene.ngeom += 1


def annotate(
    frame, front, env, title, subtitle, target_depth, target_yaw, phase, seconds
):
    canvas = Image.new("RGB", (1280, 720), BG)
    canvas.paste(Image.fromarray(frame), (0, 80))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 1279, 79), fill="#0a2029")
    draw.text((26, 14), "SimpleROV", font=font(30), fill=WHITE)
    draw.text((258, 21), title, font=font(22), fill=TEAL)
    draw.text((26, 51), subtitle, font=font(16), fill=MUTED)
    p, rpy, _, _ = env.state()
    d = env.diagnostics
    s = env.measurements()
    left = 980

    def line(y, label, value, color=WHITE):
        draw.text((left, y), label, font=font(13), fill=MUTED)
        draw.text((left, y + 19), value, font=font(22), fill=color)

    line(101, "SIMULATION TIME", f"{env.data.time:05.2f} / {seconds:.0f} s")
    line(163, "DEPTH  /  TARGET", f"{-p[2]:.3f} / {target_depth:.2f} m", ORANGE)
    line(
        225,
        "HEADING  /  TARGET",
        f"{np.rad2deg(rpy[2]):+.1f} / {np.rad2deg(target_yaw):+.1f} deg",
    )
    line(287, "WORLD POSITION  X / Y", f"{p[0]:+.2f} / {p[1]:+.2f} m")
    current = np.linalg.norm(d["current_world_m_s"])
    line(
        349,
        "CURRENT / TETHER TENSION",
        f"{current:.2f} m/s  /  {d['tether_tension_N']:.2f} N",
        TEAL,
    )
    draw.text((left, 409), "ACTUAL THRUST [N]", font=font(13), fill=MUTED)
    for i, (name, force) in enumerate(zip(["HL", "HR", "VL", "VR"], env.force)):
        x = left + i * 72
        color = "#fb807a" if env.k["thrusters"]["effectiveness"][i] == 0 else WHITE
        draw.text((x, 432), name, font=font(13), fill=MUTED)
        draw.text((x, 449), f"{force:+.2f}", font=font(17), fill=color)
    rank = env.allocator.last["rank"]
    residual = env.allocator.last["weighted_residual_norm"]
    draw.text(
        (left, 483),
        f"Allocation rank {rank} | residual {residual:.3f}",
        font=font(14),
        fill="#fb807a" if rank < 4 else MUTED,
    )
    image = Image.fromarray(front)
    image.thumbnail((272, 154))
    canvas.paste(image, (980, 533))
    draw = ImageDraw.Draw(canvas)
    draw.text((left, 511), "FORWARD CAMERA  /  IDEAL OPTICS", font=font(12), fill=MUTED)
    draw.rounded_rectangle((18, 99, 410, 135), radius=8, fill=BG)
    draw.text((30, 108), phase, font=font(17), fill=WHITE)
    draw.text(
        (22, 688),
        "MuJoCo 4.0.1  |  Sensor feedback  |  Seed 0  |  Uncalibrated model",
        font=font(14),
        fill=WHITE,
    )
    draw.text(
        (980, 699), "No waves, CFD or real optical effects", font=font(12), fill=MUTED
    )
    return np.asarray(canvas)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=12)
    parser.add_argument("--fps", type=int, default=20)
    args = parser.parse_args()
    if args.seconds < 10 or args.fps <= 0:
        raise ValueError("Use at least 10 seconds and positive fps")
    out = R / "docs/assets/videos"
    out.mkdir(parents=True, exist_ok=True)
    records = []
    previews = []
    poster = None
    source = sha(Path(__file__))
    model = display_model()
    data = mujoco.MjData(model)
    renderer = mujoco.Renderer(model, height=640, width=960)
    opt = mujoco.MjvOption()
    opt.geomgroup[:] = [1, 1, 0, 0, 0, 0]
    opt.sitegroup[:] = 0
    original_colors = model.geom_rgba.copy()
    try:
        for scenario, title, subtitle in CASES:
            env = ROV(scenario=scenario, seed=0)
            dt = env.model.opt.timestep
            stride = round(1 / args.fps / dt)
            control_stride = round(0.02 / dt)
            if abs(stride * dt - 1 / args.fps) > 1e-9:
                raise ValueError("FPS must align with physics ticks")
            target = out / (scenario + ".mp4")
            model.geom_rgba[:] = original_colors
            if scenario == "motor-fault":
                for name in ["REF_X2_H_LEFT", "REF_X2_H_LEFT_1"]:
                    gid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, name)
                    if gid >= 0:
                        model.geom_rgba[gid] = [0.80, 0.20, 0.15, 1]
            rows = []
            count = 0
            with imageio.get_writer(
                target,
                fps=args.fps,
                codec="libx264",
                quality=None,
                pixelformat="yuv420p",
                macro_block_size=16,
                ffmpeg_params=[
                    "-crf",
                    "24",
                    "-preset",
                    "medium",
                    "-movflags",
                    "+faststart",
                ],
            ) as writer:
                for tick in range(round(args.seconds / dt)):
                    t = env.data.time
                    depth = 1.2 if t < 2 else (0.95 if t < 5 else 1.2)
                    surge = 1.6 if 3 <= t < 7 else 0.0
                    yaw = 0.55 if t >= 7 else 0.0
                    if tick % control_stride == 0:
                        command = env.controller(
                            depth, surge, yaw, measurement=env.measurements()
                        )
                    env.step(command)
                    if (tick + 1) % stride:
                        continue
                    data.qpos[:] = env.data.qpos
                    data.qvel[:] = env.data.qvel
                    data.ctrl[:] = env.data.ctrl
                    data.time = env.data.time
                    mujoco.mj_forward(model, data)
                    cam = mujoco.MjvCamera()
                    cam.lookat[:] = env.data.xpos[env.bid]
                    cam.distance = 0.55
                    cam.azimuth = 135
                    cam.elevation = -23
                    renderer.update_scene(data, cam, scene_option=opt)
                    renderer.scene.flags[mujoco.mjtRndFlag.mjRND_SHADOW] = 0
                    pos = env.data.xpos[env.bid]
                    rotation = env.data.xmat[env.bid].reshape(3, 3)
                    if env.k["tether"]["enabled"]:
                        anchor = np.asarray(env.k["tether"]["anchor_world_m"])
                        point = pos + rotation @ np.asarray(
                            env.k["tether"]["attachment_body_m"]
                        )
                        color = [
                            0.45,
                            0.88,
                            0.96,
                            1 if env.diagnostics["tether_tension_N"] > 0.001 else 0.3,
                        ]
                        connector(
                            renderer.scene,
                            mujoco.mjtGeom.mjGEOM_LINE,
                            3,
                            anchor,
                            point,
                            color,
                        )
                    water = np.asarray(env.diagnostics["current_world_m_s"])
                    if np.linalg.norm(water) > 1e-3:
                        start = pos + np.array([0, 0, 0.15])
                        connector(
                            renderer.scene,
                            mujoco.mjtGeom.mjGEOM_ARROW,
                            0.003,
                            start,
                            start + water * 0.5,
                            [0.3, 0.85, 0.95, 1],
                        )
                    frame = renderer.render().copy()
                    renderer.update_scene(data, "front_camera", scene_option=opt)
                    front = renderer.render().copy()
                    phase = (
                        "Hold depth"
                        if t < 2
                        else (
                            "Ascend to 0.95 m"
                            if t < 3
                            else (
                                "Ascend + move forward"
                                if t < 5
                                else (
                                    "Descend + move forward"
                                    if t < 7
                                    else "Turn + stabilize"
                                )
                            )
                        )
                    )
                    composed = annotate(
                        frame,
                        front,
                        env,
                        title,
                        subtitle,
                        depth,
                        yaw,
                        phase,
                        args.seconds,
                    )
                    writer.append_data(composed)
                    p, r, _, _ = env.state()
                    rows.append(
                        [
                            float(env.data.time),
                            *p,
                            *r,
                            depth,
                            yaw,
                            *env.force,
                            *water,
                            env.diagnostics["tether_tension_N"],
                            env.allocator.last["weighted_residual_norm"],
                        ]
                    )
                    count += 1
                    if scenario == "pool" and count == round(6 * args.fps):
                        poster = Image.fromarray(composed)
                        poster.save(out / "poster.png")
                    # Three seconds from each actual clip form a compact animated README fallback.
                    if 3 <= env.data.time < 6 and count % max(1, args.fps // 5) == 0:
                        im = Image.fromarray(composed)
                        im.thumbnail((768, 432))
                        previews.append(
                            im.convert("P", palette=Image.Palette.ADAPTIVE, colors=128)
                        )
            with (out / (scenario + "-trace.csv")).open("w", newline="") as f:
                writer = csv.writer(f, lineterminator="\n")
                writer.writerow(
                    [
                        "time_s",
                        "x_m",
                        "y_m",
                        "z_m",
                        "roll_rad",
                        "pitch_rad",
                        "yaw_rad",
                        "target_depth_m",
                        "target_yaw_rad",
                        "H_LEFT_N",
                        "H_RIGHT_N",
                        "V_LEFT_N",
                        "V_RIGHT_N",
                        "current_x_m_s",
                        "current_y_m_s",
                        "current_z_m_s",
                        "tether_tension_N",
                        "weighted_allocation_residual",
                    ]
                )
                writer.writerows(rows)
            metadata = env.metadata()
            metadata.update(
                renderer_script_sha256=source,
                rendering={
                    "resolution": [1280, 720],
                    "fps": args.fps,
                    "frames": count,
                    "duration_s": count / args.fps,
                    "codec": "H.264 / yuv420p",
                    "display_only": "Gradient sky, lighting, tube display finish, fault highlight, straight tether diagnostic and current arrow. Physics comes from ROV; camera inset uses the actual front_camera. Propeller meshes are static.",
                },
                video_sha256=sha(target),
            )
            (out / (scenario + "-metadata.json")).write_text(
                json.dumps(metadata, indent=2) + "\n"
            )
            records.append(
                {
                    "scenario": scenario,
                    "file": str(target.relative_to(R)),
                    "duration_s": count / args.fps,
                    "frames": count,
                    "fps": args.fps,
                    "resolution": [1280, 720],
                    "sha256": sha(target),
                    "bytes": target.stat().st_size,
                }
            )
            print(scenario, count, "frames", target.stat().st_size, "bytes", flush=True)
    finally:
        renderer.close()
    concat = out / "concat.txt"
    concat.write_text("".join("file '" + case + ".mp4'\n" for case, _, _ in CASES))
    overview = out / "simple-rov-overview.mp4"
    try:
        subprocess.run(
            [
                imageio_ffmpeg.get_ffmpeg_exe(),
                "-y",
                "-loglevel",
                "error",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat),
                "-c",
                "copy",
                "-movflags",
                "+faststart",
                str(overview),
            ],
            check=True,
        )
    finally:
        concat.unlink(missing_ok=True)
    previews[0].save(
        out / "overview-preview.gif",
        save_all=True,
        append_images=previews[1:],
        duration=200,
        loop=0,
        optimize=True,
    )
    report = {
        "engine_version": "4.0.1",
        "source_script_sha256": source,
        "source_physics_sha256": env.metadata()["source_sha256"],
        "clips": records,
        "overview": {
            "file": str(overview.relative_to(R)),
            "duration_s": sum(r["duration_s"] for r in records),
            "sha256": sha(overview),
            "bytes": overview.stat().st_size,
        },
        "media_sha256": {
            str(p.relative_to(R)): sha(p) for p in sorted(out.iterdir()) if p.is_file()
        },
        "scope": "Actual uncalibrated MuJoCo trajectories. English telemetry and display diagnostics; scripted classical control, not physical robot footage. Native GitHub attachments mirror committed MP4s.",
    }
    (R / "validation/videos.json").write_text(json.dumps(report, indent=2) + "\n")
    print(
        "Overview bytes",
        overview.stat().st_size,
        "GIF bytes",
        (out / "overview-preview.gif").stat().st_size,
    )


if __name__ == "__main__":
    main()
