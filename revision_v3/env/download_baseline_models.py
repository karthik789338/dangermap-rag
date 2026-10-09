from huggingface_hub import snapshot_download
from pathlib import Path
import json
import os
import time

MODELS = [
    "Qwen/Qwen2.5-7B-Instruct",
    "Qwen/Qwen2.5-3B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "BAAI/bge-base-en-v1.5",
    "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli",
]

manifest = []

print("=" * 80)
print("DANGERMAP-RAG PHASE 0B: MODEL CACHE")
print("=" * 80)
print("HF_HOME:", os.environ.get("HF_HOME"))
print()

for i, repo_id in enumerate(MODELS, 1):
    print("=" * 80)
    print(f"[{i}/{len(MODELS)}] {repo_id}")
    print("=" * 80)

    start = time.time()

    try:
        path = snapshot_download(
            repo_id=repo_id,
            resume_download=True,
        )

        elapsed = time.time() - start

        print("CACHED:", path)
        print(f"Elapsed: {elapsed/60:.2f} minutes")

        manifest.append({
            "repo_id": repo_id,
            "status": "SUCCESS",
            "local_path": str(path),
            "elapsed_seconds": elapsed,
        })

    except Exception as exc:
        print("FAILED:", repr(exc))

        manifest.append({
            "repo_id": repo_id,
            "status": "FAILED",
            "error": repr(exc),
        })

Path("revision_v3/manifests").mkdir(parents=True, exist_ok=True)

with open(
    "revision_v3/manifests/baseline_model_cache.json",
    "w",
    encoding="utf-8",
) as f:
    json.dump(manifest, f, indent=2)

print()
print("=" * 80)

failed = [x for x in manifest if x["status"] != "SUCCESS"]

if failed:
    print("PHASE 0B MODEL CACHE: INCOMPLETE")
    for x in failed:
        print("FAILED:", x["repo_id"])
else:
    print("PHASE 0B MODEL CACHE: PASSED")

print("=" * 80)
