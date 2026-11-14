"""Decode published videos and check timing, format and source/trace consistency."""

from pathlib import Path
import argparse, csv, hashlib, json, subprocess
import imageio.v2 as imageio
import imageio_ffmpeg
import numpy as np
from PIL import Image

R = Path(__file__).resolve().parents[1]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    report = json.loads((R / "validation/videos.json").read_text())
    assert sha(R / "tools/render_videos.py") == report["source_script_sha256"]
    for name, h in report["source_physics_sha256"].items():
        assert sha(R / "simulation/mujoco" / name) == h, name
    for name, h in report["media_sha256"].items():
        assert sha(R / name) == h, name
    results = []
    for item in report["clips"] + [report["overview"]]:
        path = R / item["file"]
        reader = imageio.get_reader(path)
        meta = reader.get_meta_data()
        assert (
            meta["codec"] == "h264"
            and meta["pix_fmt"].startswith("yuv420p")
            and tuple(meta["size"]) == (1280, 720)
        )
        count, duration = imageio_ffmpeg.count_frames_and_secs(str(path))
        expected = round(item["duration_s"] * 20)
        assert count == expected and abs(duration - item["duration_s"]) < 0.06, (
            path,
            count,
            duration,
        )
        samples = [reader.get_data(i) for i in [0, count // 2, count - 1]]
        reader.close()
        assert all(np.std(x) > 20 for x in samples) and not np.array_equal(
            samples[0], samples[-1]
        )
        subprocess.run(
            [
                imageio_ffmpeg.get_ffmpeg_exe(),
                "-v",
                "error",
                "-xerror",
                "-i",
                str(path),
                "-f",
                "null",
                "-",
            ],
            check=True,
            capture_output=True,
        )
        results.append(
            {
                "file": item["file"],
                "frames": count,
                "duration_s": duration,
                "codec": meta["codec"],
                "pixel_format": meta["pix_fmt"],
                "resolution": list(meta["size"]),
                "full_decode": "PASS",
            }
        )
        if "scenario" in item:
            rows = list(
                csv.DictReader(path.with_name(item["scenario"] + "-trace.csv").open())
            )
            assert (
                len(rows) == count
                and abs(float(rows[-1]["time_s"]) - item["duration_s"]) < 1e-7
            )
            depth = -np.array([float(x["z_m"]) for x in rows])
            assert np.ptp(depth) > 0.15
            if item["scenario"] == "motor-fault":
                assert (
                    max(abs(float(x["H_LEFT_N"])) for x in rows) == 0
                    and max(float(x["weighted_allocation_residual"]) for x in rows) > 0
                )
    with Image.open(R / "docs/assets/videos/overview-preview.gif") as gif:
        assert gif.n_frames >= 50 and gif.size == (768, 432)
    j = {
        "videos": results,
        "source_sha256": {
            "tools/render_videos.py": sha(R / "tools/render_videos.py"),
            "tools/verify_videos.py": sha(Path(__file__)),
            "validation/videos.json": sha(R / "validation/videos.json"),
        },
        "gif_preview_checked": True,
        "scope": "Video decoding, timing, source and trace consistency; not physical validation.",
        "passed": True,
    }
    if args.publish:
        (R / "validation/video_checks.json").write_text(json.dumps(j, indent=2) + "\n")
    print(json.dumps(j, indent=2))


if __name__ == "__main__":
    main()
