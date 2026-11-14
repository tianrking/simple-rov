"""Launch the V5 viewer on macOS, repairing the uv-venv libpython link if needed."""
from pathlib import Path
import os
import sys
import sysconfig


def main():
    if sys.platform != 'darwin':
        raise SystemExit('This launcher is for macOS. Use python simulation/mujoco/run.py --viewer on other platforms.')
    prefix = Path(sys.prefix)
    if '--manual' in sys.argv[1:]:
        # Dedicated GLFW window must run on the real macOS main thread.
        args = sys.argv[1:]
        if '--seconds' not in args:
            args = ['--seconds', '120', *args]
        run = Path(__file__).resolve().with_name('run.py')
        os.execv(sys.executable, [sys.executable, str(run), '--viewer', *args])
    mjpython = prefix / 'bin' / 'mjpython'
    if not mjpython.is_file():
        raise SystemExit('MuJoCo launcher missing in this Python environment. Install requirements/sim.txt first.')
    library_name = sysconfig.get_config_var('LDLIBRARY')
    if library_name and library_name.endswith('.dylib') and sys.prefix != sys.base_prefix:
        target = Path(sys.base_prefix) / 'lib' / library_name
        destination = prefix / 'lib' / library_name
        if target.is_file() and not destination.exists():
            if destination.is_symlink():
                destination.unlink()  # replace only a broken symlink in the selected venv
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.symlink_to(target)
            print(f'Repaired virtualenv library link: {destination}', flush=True)
    args = sys.argv[1:]
    if '--seconds' not in args:
        args = ['--seconds', '120', *args]
    run = Path(__file__).resolve().with_name('run.py')
    print('Starting V5 Mac viewer. Close its window to stop.', flush=True)
    os.execv(str(mjpython), [str(mjpython), str(run), '--viewer', *args])


if __name__ == '__main__':
    main()
