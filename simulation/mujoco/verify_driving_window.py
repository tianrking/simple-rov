"""Native OpenGL window smoke test and callback isolation regression (no OS input injection)."""
import hashlib,json,sys
import glfw,mujoco,numpy as np
from PIL import Image
from environment import ROV,S
from manual_control import ManualControl
from desktop_viewer import DrivingWindow

env,control=ROV(),ManualControl()
window=DrivingWindow(env.model,env.data,control)
report={}
try:
    assert 'mujoco.viewer' not in sys.modules
    flags=window.scene.flags.copy();opts=window.options.flags.copy()
    for name in ['W','S','A','D','U','J','X','P',' ']:
        window.on_key(window.window,ord(name),0,glfw.PRESS,0)
        control.apply_pending(env.state())
        if name=='W':assert control.surge==2
        if name=='S':assert control.surge==-2
        window.on_key(window.window,ord(name),0,glfw.RELEASE,0)
        control.apply_pending(env.state())
        if name in ('W','S'):assert control.surge==0
        assert np.array_equal(flags,window.scene.flags) and np.array_equal(opts,window.options.flags),name
    window.on_key(window.window,glfw.KEY_W,0,glfw.PRESS,0);control.apply_pending(env.state())
    for _ in range(1000):state=env.step(env.controller(control.depth,control.surge,control.yaw))
    assert state[0][0]>.1
    window.on_focus(window.window,False);control.apply_pending(state);assert control.surge==0
    window.draw(state);window.draw(state)
    width,height=glfw.get_framebuffer_size(window.window);rgb=np.zeros((height,width,3),np.uint8)
    mujoco.mjr_readPixels(rgb,None,mujoco.MjrRect(0,0,width,height),window.context)
    Image.fromarray(rgb[::-1]).save(S.parents[1]/'docs/assets/images/driving-window.png')
    assert np.max(rgb)>100 and np.std(rgb)>10
    window.on_key(window.window,glfw.KEY_ESCAPE,0,glfw.PRESS,0)
    assert glfw.window_should_close(window.window)
    report={'dedicated_native_GLFW_window_created':True,'uses_mujoco_viewer_Simulate_hotkeys':False,
            'driving_keys_do_not_change_render_flags':True,'WS_release_zeros_surge':True,
            'losing_focus_zeros_surge':True,'ESC_closes_window':True,'forward_response_m':float(state[0][0]),
            'framebuffer_rendered':True,'framebuffer_size':[width,height],
            'scope':'Native window creation, direct callback tests (not OS key injection), water-model response and framebuffer render.',
            'source_sha256':{n:hashlib.sha256((S/n).read_bytes()).hexdigest() for n in ['desktop_viewer.py','manual_control.py','run.py','launch_macos.py']},'passed':True}
finally:window.close()
(S/'DRIVING_WINDOW_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
