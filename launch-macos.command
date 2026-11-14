#!/bin/zsh
set -e
ROV_PROJECT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
if [[ -x "$ROV_PROJECT_DIR/.venv/bin/python" ]]; then
  ROV_PYTHON="$ROV_PROJECT_DIR/.venv/bin/python"
elif [[ -n "${VIRTUAL_ENV:-}" && -x "$VIRTUAL_ENV/bin/python" ]]; then
  ROV_PYTHON="$VIRTUAL_ENV/bin/python"
else
  ROV_PYTHON="$(command -v python3)"
fi
exec "$ROV_PYTHON" "$ROV_PROJECT_DIR/simulation/mujoco/launch_macos.py" --manual "$@"
