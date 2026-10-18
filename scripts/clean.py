"""Remove only Python bytecode. Preserve all experiment evidence and waveforms."""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1]
for folder in ['scripts','tests']:
    for p in (root/folder).rglob('__pycache__'):shutil.rmtree(p);print('Removed',p)
