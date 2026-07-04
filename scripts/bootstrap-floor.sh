#!/usr/bin/env bash
# bootstrap-floor.sh — turn a fresh Ubuntu 24.04 box into an AI factory floor.
# Mirrors the proven floor2 stack: NVIDIA driver, Ollama, PyTorch, k3s agent.
#
# Usage (on the new node, as a sudoer):
#   FLOOR_NAME=floor3 K3S_URL=https://192.168.1.206:6443 K3S_TOKEN=<token> \
#     bash bootstrap-floor.sh
#
# Get the token on floor2:  sudo cat /var/lib/rancher/k3s/server/node-token
# Idempotent: safe to re-run after a failure.

set -euo pipefail

FLOOR_NAME="${FLOOR_NAME:?set FLOOR_NAME (e.g. floor3)}"
K3S_URL="${K3S_URL:-}"          # empty = skip k3s join
K3S_TOKEN="${K3S_TOKEN:-}"
OLLAMA_MODELS="${OLLAMA_MODELS:-qwen2.5:32b nomic-embed-text}"

log() { printf '\n=== [%s] %s ===\n' "$FLOOR_NAME" "$*"; }

log "hostname + basics"
sudo hostnamectl set-hostname "$FLOOR_NAME"
sudo apt-get update -qq
sudo apt-get install -y -qq build-essential curl git htop lm-sensors nvme-cli \
  python3-venv python3-pip zfsutils-linux jq

log "NVIDIA driver 535 (proven with Pascal P40 + Maxwell on floor2)"
if ! command -v nvidia-smi >/dev/null || ! nvidia-smi >/dev/null 2>&1; then
  sudo apt-get install -y -qq nvidia-driver-535-server
  echo ">>> Driver installed. REBOOT, then re-run this script. <<<"
  exit 0
fi
nvidia-smi --query-gpu=name,memory.total,temperature.gpu --format=csv

log "Ollama"
if ! command -v ollama >/dev/null; then
  curl -fsSL https://ollama.com/install.sh | sh
fi
# Listen on LAN so n8n/other floors can call it
sudo mkdir -p /etc/systemd/system/ollama.service.d
printf '[Service]\nEnvironment="OLLAMA_HOST=0.0.0.0:11434"\n' | \
  sudo tee /etc/systemd/system/ollama.service.d/lan.conf >/dev/null
sudo systemctl daemon-reload && sudo systemctl enable --now ollama
for m in $OLLAMA_MODELS; do ollama pull "$m"; done

log "PyTorch venv (CUDA 12.1 wheels; P40 = FP32/int8 workloads)"
python3 -m venv /opt/ai-venv 2>/dev/null || true
/opt/ai-venv/bin/pip install -q --upgrade pip
/opt/ai-venv/bin/pip install -q torch torchvision --index-url https://download.pytorch.org/whl/cu121
/opt/ai-venv/bin/python -c 'import torch; print("torch", torch.__version__, "cuda:", torch.cuda.is_available(), torch.cuda.device_count(), "gpu(s)")'

if [ -n "$K3S_URL" ] && [ -n "$K3S_TOKEN" ]; then
  log "k3s agent → joining $K3S_URL"
  if ! systemctl is-active --quiet k3s-agent; then
    curl -sfL https://get.k3s.io | K3S_URL="$K3S_URL" K3S_TOKEN="$K3S_TOKEN" sh -
  fi
  echo "Label from floor2:  kubectl label node $FLOOR_NAME floor=$FLOOR_NAME gpu=p40 --overwrite"
else
  log "k3s join skipped (K3S_URL/K3S_TOKEN not set)"
fi

log "done — floor '$FLOOR_NAME' is up. Point n8n HTTP nodes at http://$(hostname -I | awk '{print $1}'):11434"
