"""Run the whole pipeline: python main.py [year] [--skip-pull]

main.py (repo root or main/ folder) sets the year, runs every step inside one work folder (output/),
and renames files between steps so the scripts can find each other.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# works from the repo root or from a subfolder such as main/
ROOT = HERE if (HERE / 'data' / 'pulldata.py').exists() else HERE.parent
WORK = ROOT / 'output'
args = [a for a in sys.argv[1:] if not a.startswith('--')]
YEAR = args[0] if args else '2026'
SKIP_PULL = '--skip-pull' in sys.argv

WORK.mkdir(exist_ok=True)
if not (WORK / 'cache').exists() and (ROOT / 'cache').exists():
    shutil.copytree(ROOT / 'cache', WORK / 'cache')   # reuse already-downloaded data (no symlink: breaks git on /mnt)
env = {**os.environ, 'F1_YEAR': YEAR}


def run(script):
    print(f"\n>>> {script} (year {YEAR})")
    subprocess.run([sys.executable, str(ROOT / script)], cwd=WORK, env=env, check=True)


if SKIP_PULL:
    for f in (ROOT / 'data').glob('*.csv'):          # reuse already-pulled data
        shutil.copy(f, WORK / f.name)
else:
    run('data/pulldata.py')

run('matrixP/matrixp.py')
shutil.copy(WORK / 'performance_matrix_P.csv', WORK / f'performance_matrix_P_{YEAR}.csv')
run('weightMatrix/weightMatrix.py')
run('result/result.py')
print(f"\nAll outputs are in {WORK}")