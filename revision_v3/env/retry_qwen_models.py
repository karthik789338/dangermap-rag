from huggingface_hub import snapshot_download
from pathlib import Path
import json
import os
import time

MODELS = [
    "Qwen/Qwen2.5-7B-Instruct",
    "Qwen/Qwen2.5-3B-Instruct",
]

MAX_ATTEMPTS = 8

Path("revision_v3/manifests").mkdir(parents=True, exist_ok=True)

results = []

print("=" * 80)
print("DANGERMAP-RAG PHASE 0B-1: QWEN CACHE RECOVERY")
print("=" * 80)
print("HF_HOME:", os.environ.get("HF_HOME"))
print("HF_HUB_CACHE:", os.environ.get("HF_HUB_CACHE"))

for repo_id in MODELS:
    print()
    print("=" * 80)
    print(repo_id)
    print("=" * 80)

    success = False
    last_error = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"\nAttempt {attempt}/{MAX_ATTEMPTS}")

        try:
            start = time.time()

            path = snapshot_download(
                repo_id=repo_id,
                max_workers=1,
                ignore_patterns=[
                    "*.md",
                    ".gitattributes",
                ],
            )

            elapsed = time.time() - start

            print(f"SUCCESS: {path}")
            print(f"Elapsed: {elapsed / 60:.2f} minutes")

            results.append({
                "repo_id": repo_id,
                "status": "SUCCESS",
                "local_path": str(path),
                "revision": Path(path).name,
                "elapsed_seconds": elapsed,
            })

            success = True
            break

        except Exception as exc:
            last_error = repr(exc)
            print("FAILED:", last_error)

            if attempt < MAX_ATTEMPTS:
                wait = min(30 * attempt, 180)
                print(f"Waiting {wait}s before retry...")
                time.sleep(wait)

    if not success:
        results.append({
            "repo_id": repo_id,
            "status": "FAILED",
            "error": last_error,
        })

with open(
    "revision_v3/manifests/qwen_model_cache.json",
    "w",
    encoding="utf-8",
) as f:
    json.dump(results, f, indent=2)

print()
print("=" * 80)

failed = [r for r in results if r["status"] != "SUCCESS"]

if failed:
    print("PHASE 0B-1: INCOMPLETE")
    for r in failed:
        print("FAILED:", r["repo_id"])
else:
    print("PHASE 0B-1: PASSED")

print("=" * 80)
