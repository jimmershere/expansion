#!/usr/bin/env bash
# p40-health.sh — GPU thermal/throttle watchdog, JSON output for n8n.
# Cron it or curl it from an n8n Schedule trigger via ssh/Execute Command.
# Exit 1 if any GPU is missing-from-driver or >=85C (P40 throttles ~89C).

set -uo pipefail
LIMIT="${LIMIT:-85}"

expected=$(lspci | grep -ci -E 'nvidia.*(3d|vga)' || true)
visible=$(nvidia-smi --query-gpu=count --format=csv,noheader 2>/dev/null | head -1 || echo 0)

rows=$(nvidia-smi --query-gpu=index,name,temperature.gpu,power.draw,utilization.gpu,memory.used --format=csv,noheader 2>/dev/null || true)

status=ok; hot=0
while IFS=, read -r idx name temp rest; do
  t=$(echo "$temp" | tr -dc '0-9')
  [ -n "$t" ] && [ "$t" -ge "$LIMIT" ] && { status=hot; hot=$((hot+1)); }
done <<< "$rows"
[ "$visible" -lt "$expected" ] && status=missing_gpu

jq -n --arg host "$(hostname)" --arg status "$status" \
      --argjson expected "$expected" --argjson visible "${visible:-0}" \
      --arg gpus "$rows" \
      '{host:$host, status:$status, gpus_on_bus:$expected, gpus_in_driver:$visible, detail:$gpus, ts:now|todate}'

[ "$status" = ok ]
