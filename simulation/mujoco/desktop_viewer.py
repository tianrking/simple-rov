"""Dedicated GLFW driving window. No mujoco.viewer/Simulate hotkey dispatch."""
import glfw
import mujoco


class DrivingWindow:
    def __init__(self, model, data, controls):
        self.model, self.data, self.controls = model, data, controls
        if not glfw.init():
            raise RuntimeError('GLFW initialization failed; run on a local desktop.')
        self.window = glfw.create_window(1200, 850, 'SimpleROV-4 | Dedicated Driving Window', None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError('Cannot create OpenGL window.')
        glfw.make_context_current(self.window)
        glfw.swap_interval(0)
        self.scene = mujoco.MjvScene(model, maxgeom=10000)
        self.context = mujoco.MjrContext(model, mujoco.mjtFontScale.mjFONTSCALE_100)
        self.camera = mujoco.MjvCamera()
        self.camera.distance, self.camera.elevation, self.camera.azimuth = .7, -24, 125
        self.options = mujoco.MjvOption()
        self.options.geomgroup[3] = 0
        self.last_cursor = glfw.get_cursor_pos(self.window)
        glfw.set_key_callback(self.window, self.on_key)
        glfw.set_window_focus_callback(self.window, self.on_focus)
        glfw.set_cursor_pos_callback(self.window, self.on_cursor)
        glfw.set_scroll_callback(self.window, self.on_scroll)
        glfw.show_window(self.window)

    def on_key(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(window, True)
        elif action in (glfw.PRESS, glfw.RELEASE):
            self.controls.key_callback(key, action == glfw.PRESS)

    def on_focus(self, window, focused):
        if not focused:
            self.controls.release_motion()

    def on_cursor(self, window, x, y):
        dx, dy = x - self.last_cursor[0], y - self.last_cursor[1]
        self.last_cursor = (x, y)
        height = max(1, glfw.get_window_size(window)[1])
        if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
            mujoco.mjv_moveCamera(self.model, mujoco.mjtMouse.mjMOUSE_ROTATE_V,
                                  dx / height, dy / height, self.scene, self.camera)

    def on_scroll(self, window, dx, dy):
        mujoco.mjv_moveCamera(self.model, mujoco.mjtMouse.mjMOUSE_ZOOM,
                              0, -.05 * dy, self.scene, self.camera)
        self.camera.distance = max(.2, min(8., self.camera.distance))

    def poll(self):
        glfw.poll_events()
        return not glfw.window_should_close(self.window)

    def draw(self, state):
        self.camera.lookat[:] = state[0]
        width, height = glfw.get_framebuffer_size(self.window)
        if not width or not height:
            return
        viewport = mujoco.MjrRect(0, 0, width, height)
        mujoco.mjv_updateScene(self.model, self.data, self.options, None, self.camera,
                              mujoco.mjtCatBit.mjCAT_ALL, self.scene)
        mujoco.mjr_render(viewport, self.scene, self.context)
        mujoco.mjr_overlay(mujoco.mjtFont.mjFONT_NORMAL, mujoco.mjtGridPos.mjGRID_TOPLEFT,
                            viewport, self.controls.label(state), '', self.context)
        glfw.swap_buffers(self.window)

    def close(self):
        self.context.free()
        glfw.destroy_window(self.window)
        glfw.terminate()
