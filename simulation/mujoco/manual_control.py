"""Discrete keyboard setpoints; callbacks enqueue events, physics thread applies them."""
from dataclasses import dataclass
from queue import SimpleQueue, Empty
import math


@dataclass
class ManualControl:
    depth: float = 1.2
    surge: float = 0.0
    yaw: float = 0.0

    def __post_init__(self):
        self.events = SimpleQueue()
        self.held = set()

    def key_callback(self, keycode, pressed=True):
        self.events.put((keycode, pressed))

    def release_motion(self):
        self.events.put((None, False))

    def apply_pending(self, state):
        changed = False
        while True:
            try:
                code, pressed = self.events.get_nowait()
            except Empty:
                break
            if code is None:
                self.held.clear()
                self.surge = 0.0
                changed = True
                continue
            key = chr(code).upper() if 0 <= code < 128 else ''
            if key in ('W', 'S'):
                if pressed:
                    self.held.add(key)
                else:
                    self.held.discard(key)
                self.surge = 2.0 * (('W' in self.held) - ('S' in self.held))
                changed = True
                continue
            if not pressed:
                continue
            if key in ('A', 'D'):
                self.yaw += math.radians(15) * (1 if key == 'A' else -1)
                self.yaw = math.atan2(math.sin(self.yaw), math.cos(self.yaw))
            elif key in ('U', 'J'):
                self.depth = min(2.5, max(0.35, self.depth + (-0.1 if key == 'U' else 0.1)))
            elif key == 'X':
                self.held.clear()
                self.surge = 0.0
                self.depth = min(2.5, max(0.35, -float(state[0][2])))
                self.yaw = float(state[1][2])
            else:
                continue
            changed = True
        return changed

    def label(self, state):
        return ('Hold W/S: forward/reverse | X: hold depth/heading\n'
                'A/D: turn 15 deg | U/J: ascend/descend 0.1 m\n'
                'Release W/S or leave window: zero surge. ESC: exit.\n'
                f'Depth target/actual: {self.depth:.2f} / {-state[0][2]:.2f} m\n'
                f'Surge command: {self.surge:+.1f} N | Heading target: {math.degrees(self.yaw):+.0f} deg\n'
                f'World position: X {state[0][0]:+.2f} Y {state[0][1]:+.2f} Z {state[0][2]:+.2f} m')
