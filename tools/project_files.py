"""Deterministic public project file inventory, excluding local/private runtime data."""
from pathlib import Path
import os
ROOT=Path(__file__).resolve().parents[1]
EXCLUDE_DIRS={'.git','.venv','venv','runs','__pycache__','.pytest_cache','.mypy_cache','.ruff_cache','.idea','.vscode'}
EXCLUDE_NAMES={'.DS_Store','MANIFEST.sha256.json','MUJOCO_LOG.TXT'}
def project_files():
    for base,dirs,names in os.walk(ROOT):
        dirs[:]=sorted(d for d in dirs if d not in EXCLUDE_DIRS and not d.endswith('-backups'))
        for name in sorted(names):
            if name in EXCLUDE_NAMES or name.startswith('.env') or name.endswith(('.pyc','.pem','.key','.bak','.lck','.tmp')):continue
            p=Path(base)/name
            if p.is_symlink():raise RuntimeError('Unexpected publication symlink: '+str(p.relative_to(ROOT)))
            yield p
