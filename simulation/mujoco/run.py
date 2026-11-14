"""V5 automatic demonstration or keyboard setpoint control."""
import argparse
import csv
import json
import time
from pathlib import Path
from datetime import datetime, timezone

import mujoco
from environment import ROV, S
from manual_control import ManualControl


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--viewer', action='store_true')
    parser.add_argument('--manual', action='store_true', help='Keyboard setpoints; requires --viewer')
    parser.add_argument('--render', action='store_true')
    parser.add_argument('--output-dir', type=Path, default=None)
    parser.add_argument('--seconds', type=float, default=16)
    args = parser.parse_args()
    if args.manual and not args.viewer:
        parser.error('--manual requires --viewer')
    if args.seconds <= 0:
        parser.error('--seconds must be positive')
    output = args.output_dir or S.parents[1] / 'runs' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
    output.mkdir(parents=True, exist_ok=True)
    env = ROV()
    dt = env.model.opt.timestep
    manual = ManualControl() if args.manual else None
    rows, frames = [], []
    viewer = renderer = driving = None
    state = env.state()
    if manual:
        from desktop_viewer import DrivingWindow
        driving = DrivingWindow(env.model, env.data, manual)
    elif args.viewer:
        from mujoco import viewer as mjviewer
        viewer = mjviewer.launch_passive(
            env.model, env.data,
            key_callback=manual.key_callback if manual else None,
            show_left_ui=False, show_right_ui=False)
        viewer.cam.distance = .65
        viewer.cam.elevation = -20
        viewer.cam.azimuth = 125
        viewer.opt.geomgroup[3] = 0
    if args.render:
        renderer = mujoco.Renderer(env.model, height=480, width=640)
        opt = mujoco.MjvOption()
        opt.geomgroup[3] = 0
    if manual:
        print('MANUAL: W/S forward/reverse; A/D heading; U/J depth; X zero surge and hold current depth/heading.\n'
              'Hold W/S to move, release to zero surge. Losing focus also zeros surge. X does not hold horizontal position.', flush=True)
    try:
        for i in range(int(args.seconds / dt)):
            if driving and i % 10 == 0 and not driving.poll():
                break
            if viewer and i % 10 == 0 and not viewer.is_running():
                break
            t = i * dt
            if manual:
                if manual.apply_pending(state):
                    print(manual.label(state), flush=True)
                depth, surge, yaw = manual.depth, manual.surge, manual.yaw
            else:
                depth = 1.2 if t < 3 else (.9 if t < 7 else 1.2)
                surge = 0 if t < 5 else (2 if t < 10 else 0)
                yaw = 0 if t < 9 else .8
            state = env.step(env.controller(depth, surge, yaw))
            pos, rpy, velocity, omega = state
            if i % 25 == 0:
                rows.append([t, *pos, *rpy, *env.force])
            if viewer and i % 10 == 0:
                with viewer.lock():
                    viewer.cam.lookat[:] = pos
                text = manual.label(state) if manual else 'AUTO DEMO | Add --manual for keyboard control'
                viewer.set_texts((mujoco.mjtFontScale.mjFONTSCALE_100,
                                  mujoco.mjtGridPos.mjGRID_TOPLEFT, text, ''))
                viewer.sync()
                time.sleep(dt * 10)
            if driving and i % 10 == 0:
                driving.draw(state)
                time.sleep(dt * 10)
            if renderer and i % 50 == 0:
                cam = mujoco.MjvCamera()
                cam.lookat[:] = pos
                cam.distance, cam.azimuth, cam.elevation = .6, 130, -24
                renderer.update_scene(env.data, cam, scene_option=opt)
                frames.append(renderer.render().copy())
        name = 'manual_states.csv' if manual else ('demo_states.csv' if args.render else 'viewer_states.csv')
        with (output / name).open('w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['time_s','x_m','y_m','z_m','roll_rad','pitch_rad','yaw_rad',
                             'H_LEFT_N','H_RIGHT_N','V_LEFT_N','V_RIGHT_N'])
            writer.writerows(rows)
        if renderer and frames:
            from PIL import Image
            import imageio.v2 as imageio
            Image.fromarray(frames[-1]).save(output / 'MuJoCo_V5.png')
            renderer.update_scene(env.data, 'front_camera', scene_option=opt)
            Image.fromarray(renderer.render()).save(output / 'MuJoCo_前视.png')
            imageio.mimsave(output / 'V5_sim_demo.mp4', frames, fps=10, macro_block_size=16)
        print(json.dumps({'output_directory': str(output.resolve()),
                          'mode': 'manual_setpoints' if manual else 'automatic_demo',
                          'simulated_seconds': env.data.time,
                          'final_position_m': state[0].tolist(),
                          'final_rpy_rad': state[1].tolist(),
                          'mass_and_hydrodynamics': 'assumed, not calibrated'}, indent=2))
    finally:
        if driving:
            driving.close()
        if viewer:
            viewer.close()
        if renderer:
            renderer.close()


if __name__ == '__main__':
    main()
