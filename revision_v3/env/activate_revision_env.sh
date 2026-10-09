export DANGERMAP_ROOT="$HOME/dangermap-rag"

# Keep the cache already populated on this machine.
export HF_HOME="$HOME/.cache/huggingface"
export HF_HUB_CACHE="$HF_HOME/hub"
export HF_DATASETS_CACHE="$HF_HOME/datasets"
export SENTENCE_TRANSFORMERS_HOME="$HF_HOME/sentence_transformers"
export TORCH_HOME="$HOME/.cache/torch"

# More tolerant downloads on remote/cloud nodes.
export HF_HUB_ETAG_TIMEOUT=120
export HF_HUB_DOWNLOAD_TIMEOUT=1200
export TOKENIZERS_PARALLELISM=false
