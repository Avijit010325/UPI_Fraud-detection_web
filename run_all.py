"""Run the whole pipeline in order:  python run_all.py   (about 2-3 minutes)"""
import subprocess
import sys
import time

SCRIPTS = [
    "00_Dataset_Selection.py",
    "01_NumPy_Foundations.py",
    "02_Pandas_DataCleaning.py",
    "03_Visualization.py",
    "04_Encoding_Preprocessing.py",
    "05_KMeans_Unsupervised.py",
    "06_SupervisedModels.py",
]

for name in SCRIPTS:
    print(f"\n{'#' * 78}\n# {name}\n{'#' * 78}", flush=True)
    t0 = time.time()
    result = subprocess.run([sys.executable, "-W", "ignore", name])
    if result.returncode != 0:
        sys.exit(f"\n{name} failed (exit code {result.returncode}). Fix it before continuing.")
    print(f"\n[{name} finished in {time.time() - t0:.0f}s]", flush=True)

print("\nAll scripts finished. Start the web app with:  python app/app.py")
