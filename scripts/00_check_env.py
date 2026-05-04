import os
import shutil
import sys

print("=" * 80)
print("DangerMap-RAG environment check")
print("=" * 80)

print("Python:", sys.version)
print("Working directory:", os.getcwd())

try:
    import torch
    print("Torch:", torch.__version__)
    print("CUDA available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("GPU count:", torch.cuda.device_count())
        print("GPU name:", torch.cuda.get_device_name(0))
        print("CUDA version:", torch.version.cuda)
        free, total = torch.cuda.mem_get_info()
        print(f"GPU memory free/total: {free / 1e9:.2f} GB / {total / 1e9:.2f} GB")
except Exception as e:
    print("Torch check failed:", repr(e))

packages = [
    "transformers",
    "accelerate",
    "sentence_transformers",
    "datasets",
    "pandas",
    "numpy",
    "sklearn",
    "tqdm",
]

print("\nPackage imports:")
for pkg in packages:
    try:
        __import__(pkg)
        print(f"  OK: {pkg}")
    except Exception as e:
        print(f"  FAIL: {pkg} -> {repr(e)}")

usage = shutil.disk_usage(".")
print("\nDisk:")
print(f"  Total: {usage.total / 1e9:.2f} GB")
print(f"  Used : {usage.used / 1e9:.2f} GB")
print(f"  Free : {usage.free / 1e9:.2f} GB")

print("\nDone.")
