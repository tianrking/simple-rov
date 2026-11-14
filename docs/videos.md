# Simulation video gallery

Real MuJoCo 4.0.1 trajectories, 1280 × 720 H.264 at 20 fps. All four scenarios use the foam-free standard assembly, sensor feedback, 500 Hz physics, 50 Hz control and seed 0. Parameters remain uncalibrated. These show scripted classical-control commands, not physical robot footage.

## Overview

https://github.com/user-attachments/assets/2bf94293-84e5-456a-9249-f08cb007cc9f

[Download the 48-second MP4](assets/videos/simple-rov-overview.mp4) · [Animated preview](assets/videos/overview-preview.gif)

| Chapter | Time |
|---|---|
| Basic movement | 00:00-00:12 |
| Cross-current | 00:12-00:24 |
| Lumped tether | 00:24-00:36 |
| H_LEFT disabled | 00:36-00:48 |

## Basic movement

Depth steps, forward surge, a heading change and stabilization.

https://github.com/user-attachments/assets/14b246bd-16ec-4847-b6e0-367b2e263e27

[MP4 original](assets/videos/pool.mp4) · [State trace](assets/videos/pool-trace.csv) · [Resolved parameters and source hashes](assets/videos/pool-metadata.json)

## Water current

An arrow shows local water velocity. The vehicle drifts laterally because it has no independent sway actuator.

https://github.com/user-attachments/assets/1454e87d-76c1-463d-bccc-eb611f41d231

[MP4 original](assets/videos/cross-current.mp4) · [State trace](assets/videos/cross-current-trace.csv) · [Resolved parameters and source hashes](assets/videos/cross-current-metadata.json)

## Tether load

A straight diagnostic link joins the configured anchor and chassis eye. Tension is real model output; a slack link fades. It is not a distributed cable shape.

https://github.com/user-attachments/assets/682f9a95-4fbe-4be1-8633-97d2394cfdbf

[MP4 original](assets/videos/tethered.mp4) · [State trace](assets/videos/tethered-trace.csv) · [Resolved parameters and source hashes](assets/videos/tethered-metadata.json)

## Motor failure

H_LEFT is disabled. The panel shows zero actual thrust, allocation rank three and residual error. Four-axis control is no longer fully achievable.

https://github.com/user-attachments/assets/84ad992a-7746-449a-a80a-532b0f8b8e52

[MP4 original](assets/videos/motor-fault.mp4) · [State trace](assets/videos/motor-fault-trace.csv) · [Resolved parameters and source hashes](assets/videos/motor-fault-metadata.json)

## What the display means

- Depth and heading are shown beside the controller targets; world position is ground truth.
- The force panel shows actual delayed/rate-limited model thrust, not nominal commands or electrical current.
- The forward-camera inset is the model's actual `front_camera`, without realistic refraction or turbidity.
- The current arrow and straight tether link are display diagnostics. They do not add forces to the plant.
- Sky color, lighting, tube display finish and the failed-motor highlight are presentation changes only. Propeller meshes are static; thrust is applied at the modeled sites.
- Values are in SI. No battery/ESC power model, waves or CFD are implied.

## Reproduce the published videos

From the repository root, after installing `requirements/sim.txt`:

```bash
python tools/render_videos.py
python tools/verify_videos.py
```

The renderer produces four 12-second clips, the 48-second overview, a 12-second animated preview, poster, traces and metadata. It uses the same `ROV` physics/control implementation as the simulator. Normal individual recordings are also available with:

```bash
python simulation/mujoco/run.py --render --scenario cross-current --output-dir runs/current-video
```

The normal runner uses its own demonstration sequence; `tools/render_videos.py` reproduces the specifically published presentation sequence. Neither command depends on GitHub media hosting.

[Renderer source](../tools/render_videos.py) · [Video checks](../validation/video_checks.json) · [Media inventory and hashes](../validation/videos.json) · [GitHub hosting record](../validation/video_hosting.json) · [Simulation foundation](simulation-foundation.md).

GitHub-native assets are mirrored from the committed MP4 originals. Offline HTML pages use the local MP4 files with standard player controls; no external host is required. The animated fallback remains available on Markdown mirrors without a native player.
