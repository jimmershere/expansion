# floor2 Audit — 2026-07-04 (192.168.1.206)

## Platform

- **Chassis:** Dell Precision Tower 7910 (T7910)
- **CPU:** 2× Xeon E5-2650 v3 @ 2.30GHz — 20 cores / 40 threads
- **RAM:** 128GB (117Gi usable), 85Gi available under load avg ~6
- **Storage:** ZFS rpool 338G (37% used) + LVM volumes 712G + 8.2TB + SK hynix 512G + Crucial MX500 500G SSDs
- **OS:** Ubuntu 24.04.4, kernel 6.17, uptime 37 days
- **NVIDIA driver:** 535.309.01

## GPUs

| Slot | Card | State |
|---|---|---|
| 0000:02:00.0 (CPU0) | GTX Titan X 12GB (Maxwell) | **Working.** 37°C idle, 16W, 289MiB used |
| 0000:03:00.0 (CPU0) | Tesla P40 24GB | **Dead to driver** — "Unable to determine the device handle: Unknown Error", Video BIOS `??.??` (never initializes) |
| 0000:a1:00.0 (CPU1) | Tesla P40 24GB | **Dead to driver** — same failure |

Diagnosis: both P40s enumerate on the PCI bus but the driver cannot bring them
up. P40s are **passively cooled server cards** that require ducted front-to-back
forced air (they have no fans). The T7910 GPU bays don't deliver it; consistent
with the known thermal history. The Titan X (active cooler) is happy in the same
chassis, so chassis airflow/PSU are not the issue — it's card-level cooling.
A secondary suspect is aux power: P40 takes an **8-pin CPU/EPS connector**, not
PCIe 8-pin; wrong or missing adapters produce exactly this never-initializes
signature. Verify connector type during teardown.

Maintenance-window checks (requires user-approved window; blocked from doing
live because n8n/k3s run here):

1. `echo 1 > /sys/bus/pci/devices/0000:03:00.0/remove && echo 1 > /sys/bus/pci/rescan` — see if a card re-inits cold
2. Reboot → watch `dmesg` for NVRM/Xid lines during driver bring-up
3. Physically confirm EPS vs PCIe power plugs on both P40s
4. Pull both P40s for relocation (see proposal) — they will never be reliable in this chassis without blower kits

## Software stack (keep running — this is the orchestration floor)

- k3s v1.35.4 single node, API :6443 — namespaces: argocd (7 pods, ArgoCD GitOps),
  kube-system (traefik/coredns/metrics), dev-core, dev-hello (sandbox), resume-tailor, triage-report
- n8n 2.26.7 (systemd, :5678) — active; AI + k8s training workflows
- Ollama :11434 — qwen2.5 3b/7b/32b, qwen3:14b, qwen2.5-coder:7b, deepseek-r1:7b, nomic-embed-text
- Qdrant :6333
