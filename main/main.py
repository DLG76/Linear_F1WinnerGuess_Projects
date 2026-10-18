"""Run the whole pipeline in order:
    python3 main/main.py          # uses the CSV files already in data/
    python3 main/main.py --pull   # download the quali data again first (needs fastf1 + working F1 API)

Steps: pulldata -> matrixp -> weightMatrix -> result
Everything runs inside <repo>/output/ so the scripts find each other's files.
The year is read from TARGET_YEAR in result/result.py (data year; the prediction is for year + 1).
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent if HERE.name == 'main' else HERE
WORK = ROOT / 'output'
WORK.mkdir(exist_ok=True)

YEAR = re.search(r'^TARGET_YEAR\s*=\s*(\d+)', (ROOT / 'result' / 'result.py').read_text(), re.M).group(1)


def run(script):
    print(f"\n>>> {script}")
    subprocess.run([sys.executable, str(ROOT / script)], cwd=WORK, check=True)


if '--pull' in sys.argv:
    if (ROOT / 'cache').exists() and not (WORK / 'cache').exists():
        shutil.copytree(ROOT / 'cache', WORK / 'cache')
    run('data/pulldata.py')
else:
    for f in (ROOT / 'data').glob('*.csv'):
        shutil.copy(f, WORK / f.name)

run('matrixP/matrixp.py')
# matrixp.py writes performance_matrix_P.csv but result.py reads performance_matrix_P_<year>.csv
shutil.copy(WORK / 'performance_matrix_P.csv', WORK / f'performance_matrix_P_{YEAR}.csv')
run('weightMatrix/weightMatrix.py')
run('result/result.py')

print(f"\nAll outputs are in {WORK}")