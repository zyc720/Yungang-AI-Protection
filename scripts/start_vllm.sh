#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# start_vllm.sh — Launch a local vLLM OpenAI-compatible API server for the
# Yungang Dictionary RAG system.
#
# Usage:
#   chmod +x scripts/start_vllm.sh
#   ./scripts/start_vllm.sh
#
# The server listens on http://0.0.0.0:8002/v1 and speaks the OpenAI
# chat/completions protocol. Set LLM_PROVIDER=vllm in backend/.env to
# route the RAG pipeline through this server.
#
# Environment variables (all optional, with sensible defaults):
#   VLLM_PORT             - API server port (default: 8002)
#   VLLM_HOST             - Bind address (default: 0.0.0.0)
#   VLLM_MODEL            - HuggingFace model ID or local path
#   VLLM_GPU_MEM_UTIL     - GPU memory utilization fraction (default: 0.90)
#   VLLM_MAX_MODEL_LEN    - Max sequence length (default: 8192)
#   VLLM_DTYPE            - Data type: auto, float16, bfloat16 (default: auto)
#   VLLM_CONDA_ENV        - Conda environment name (default: vllm_env)
#   CONDA_BASE            - Anaconda/miniconda install path (default: $HOME/anaconda3)

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration — tune these to match your hardware
# ---------------------------------------------------------------------------
MODEL="${VLLM_MODEL:-casperhansen/deepseek-r1-distill-qwen-32b-awq}"
PORT="${VLLM_PORT:-8002}"
HOST="${VLLM_HOST:-0.0.0.0}"
GPU_MEM="${VLLM_GPU_MEM_UTIL:-0.90}"
MAX_MODEL_LEN="${VLLM_MAX_MODEL_LEN:-8192}"
DTYPE="${VLLM_DTYPE:-auto}"

# ---------------------------------------------------------------------------
# Conda environment (must have vllm installed)
# ---------------------------------------------------------------------------
CONDA_ENV="${VLLM_CONDA_ENV:-vllm_env}"
CONDA_BASE="${CONDA_BASE:-$HOME/anaconda3}"

# Resolve the conda environment's Python so we can find its vllm binary.
_VLLM_PYTHON="${CONDA_BASE}/envs/${CONDA_ENV}/bin/python"

if [ ! -x "${_VLLM_PYTHON}" ]; then
    echo "ERROR: conda env '${CONDA_ENV}' not found at ${_VLLM_PYTHON}" >&2
    echo "Set VLLM_CONDA_ENV to the name of a conda environment with vllm installed." >&2
    exit 1
fi

_VLLM_BIN="$("${_VLLM_PYTHON}" -c "import shutil; print(shutil.which('vllm') or '')" 2>/dev/null)"
# Fallback: vllm is usually in the same bin directory as the env Python
if [ -z "${_VLLM_BIN}" ] && [ -x "${CONDA_BASE}/envs/${CONDA_ENV}/bin/vllm" ]; then
    _VLLM_BIN="${CONDA_BASE}/envs/${CONDA_ENV}/bin/vllm"
fi

if [ -z "${_VLLM_BIN}" ] || [ ! -x "${_VLLM_BIN}" ]; then
    echo "ERROR: vllm CLI not found in conda env '${CONDA_ENV}'." >&2
    echo "Install it with: pip install vllm" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------
if ! nvidia-smi &>/dev/null; then
    echo "ERROR: nvidia-smi not found. Is the NVIDIA driver installed?" >&2
    exit 1
fi

if lsof -i ":${PORT}" &>/dev/null 2>&1; then
    echo "ERROR: port ${PORT} is already in use." >&2
    echo "Check with: lsof -i :${PORT}" >&2
    echo "Set VLLM_PORT to a different port." >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Launch
# ---------------------------------------------------------------------------
echo "============================================"
echo "  vLLM OpenAI-compatible Server"
echo "  Yungang Dictionary RAG System"
echo "============================================"
echo "  Model:        ${MODEL}"
echo "  Port:         ${PORT}"
echo "  Host:         ${HOST}"
echo "  GPU mem util: ${GPU_MEM}"
echo "  Max len:      ${MAX_MODEL_LEN}"
echo "  Dtype:        ${DTYPE}"
echo "  Conda env:    ${CONDA_ENV}"
echo "  vLLM binary:  ${_VLLM_BIN}"
echo "  API base:     http://${HOST}:${PORT}/v1"
echo "============================================"
echo ""

# Force offline mode — the model is already cached locally.
export HF_HUB_OFFLINE=1

# Ensure the conda env bin is on PATH so the EngineCore subprocess can
# find tools like ninja (required by FlashInfer JIT compilation).
export PATH="${CONDA_BASE}/envs/${CONDA_ENV}/bin:${PATH}"

exec "${_VLLM_BIN}" serve "${MODEL}" \
    --host "${HOST}" \
    --port "${PORT}" \
    --dtype "${DTYPE}" \
    --gpu-memory-utilization "${GPU_MEM}" \
    --max-model-len "${MAX_MODEL_LEN}" \
    --trust-remote-code
