"""Run the whole pipeline in order:
    python3 main/main.py          # uses the CSV files already in data/
    python3 main/main.py --pull   # download the quali data again first (needs fastf1 + working F1 API)

Steps: pulldata -> matrixp -> weightMatrix -> result
Settings live in <repo>/config.py:
    TARGET_YEAR  year of the qualifying data
    DRIVERS      the 7 drivers to compare (None = top 7 of qualifying)
pulldata saves telemetry of ALL drivers; the 7 compared drivers are picked from them.
Everything runs inside <repo>/output/ so the scripts find each other's files.
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent if HERE.name == 'main' else HERE
sys.path.insert(0, str(ROOT))
from config import TARGET_YEAR
try:
    from config import DRIVERS
except ImportError:
    DRIVERS = None

N_DRIVERS = 7 

WORK = ROOT / 'output'
WORK.mkdir(exist_ok=True)
DATA = ROOT / 'data'

TELEMETRY_NAME = f'singapore_q_{TARGET_YEAR}_data.csv'
LEGACY_TELEMETRY_NAME = f'singapore_q_top7_{TARGET_YEAR}_data.csv'
CORNERS_NAME = f'singapore_{TARGET_YEAR}_corners.csv'


def run(script):
    print(f"\n>>> {script}")
    subprocess.run([sys.executable, str(ROOT / script)], cwd=WORK, check=True)


def telemetry_path():
    for name in (TELEMETRY_NAME, LEGACY_TELEMETRY_NAME):
        if (DATA / name).exists():
            return DATA / name
    return None


def drivers_in(path):
    return pd.read_csv(path, usecols=['Driver'])['Driver'].unique().tolist()


def data_ready():
    if not (DATA / CORNERS_NAME).exists():
        return False
    if (DATA / TELEMETRY_NAME).exists():
        return True    
    legacy = DATA / LEGACY_TELEMETRY_NAME 
    return legacy.exists() and set(DRIVERS or []) <= set(drivers_in(legacy))


print(f"TARGET_YEAR = {TARGET_YEAR}")

pulled = False
if '--pull' in sys.argv:
    run('data/pulldata.py')
    pulled = True
elif not data_ready():
    print(f"ไฟล์ข้อมูลของปี {TARGET_YEAR} ยังไม่มี หรือไม่มีนักแข่งที่เลือกครบ -> ดึงข้อมูลอัตโนมัติ")
    run('data/pulldata.py')
    pulled = True

tel_file = telemetry_path()
if tel_file is None or not (DATA / CORNERS_NAME).exists():
    sys.exit(f"\nดึงข้อมูลแล้วแต่ยังไม่พบไฟล์ของปี {TARGET_YEAR} ใน {DATA}")

available = drivers_in(tel_file)
chosen = list(DRIVERS) if DRIVERS else available[:N_DRIVERS]

problems = []
if len(chosen) != N_DRIVERS:
    problems.append(f"ต้องเลือกนักแข่ง {N_DRIVERS} คน แต่ได้ {len(chosen)} คน")
if len(set(chosen)) != len(chosen):
    problems.append("มีนักแข่งซ้ำกันในรายการ")
unknown = [d for d in chosen if d not in available]
if unknown:
    problems.append(f"ไม่พบในข้อมูล: {unknown}")
if problems:
    sys.exit("\nเลือกนักแข่งไม่ถูกต้อง:\n  " + "\n  ".join(problems) +
             f"\nนักแข่งที่มีในข้อมูลปี {TARGET_YEAR} (เรียงตามอันดับควอลิฟาย):\n  {available}")

print(f"นักแข่งที่เอามาเทียบ: {chosen}")

shutil.copy(tel_file, WORK / TELEMETRY_NAME)
shutil.copy(DATA / CORNERS_NAME, WORK / CORNERS_NAME)

run('matrixP/matrixp.py')
run('weightMatrix/weightMatrix.py')
run('result/result.py')

print(f"\nAll outputs are in {WORK}")