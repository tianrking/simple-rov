"""Regression: keyboard setpoints produce intended water-model motion."""
import hashlib
import json
import math
from environment import ROV, S
from manual_control import ManualControl

results = {}
for key, axis, sign in [('W',0,1),('S',0,-1),('U',2,1),('J',2,-1),('A',5,1),('D',5,-1)]:
    env, command = ROV(), ManualControl()
    p0, r0, _, _ = env.state()
    command.key_callback(ord(key))
    assert command.apply_pending(env.state())
    for _ in range(1500):
        state = env.step(env.controller(command.depth, command.surge, command.yaw))
    change = (state[0][axis] - p0[axis]) if axis < 3 else state[1][axis-3] - r0[axis-3]
    assert change * sign > .02, (key, change)
    results[key] = float(change)
env, command = ROV(), ManualControl()
command.key_callback(ord('W')); command.apply_pending(env.state())
for _ in range(800):state = env.step(env.controller(command.depth, command.surge, command.yaw))
command.key_callback(ord('X')); command.apply_pending(state)
assert command.surge == 0 and abs(command.depth + state[0][2]) < 1e-9
assert abs(command.yaw - state[1][2]) < 1e-9
results['X_holds_current_depth_heading_with_zero_surge'] = True
command.key_callback(ord('W'));command.apply_pending(state);assert command.surge==2
command.key_callback(ord('W'), False);command.apply_pending(state);assert command.surge==0
command.key_callback(ord('S'));command.apply_pending(state);assert command.surge==-2
command.release_motion();command.apply_pending(state);assert command.surge==0
results['WS_release_and_focus_loss_zero_surge']=True
for key, expected in [('U', .35), ('J',2.5)]:
    for _ in range(100):command.key_callback(ord(key))
    command.apply_pending(env.state()); assert abs(command.depth-expected)<1e-9
results['depth_command_clamp_m'] = [.35,2.5]
results['source_sha256'] = {n:hashlib.sha256((S/n).read_bytes()).hexdigest() for n in ['run.py','manual_control.py','environment.py']}
results['scope'] = 'Keyboard command mapping and response under the existing assumed water model. Not physical robot validation.'
results['passed'] = True
(S/'MANUAL_CONTROL_CHECKS.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
