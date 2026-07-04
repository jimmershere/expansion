# Expansion Proposal — More Floors for the AI Factory

**Date:** 2026-07-04 · **Owner:** Jimmer · **Prepared by:** Claude
**Goal:** Turn the Apr–Jul hardware haul + the thermally-stranded floor2 P40s into
1–2 new "floors" (AI full-stack dev factories) running the proven floor2 stack:
Ubuntu 24.04 · NVIDIA · Ollama · PyTorch · k3s · n8n · Qdrant · ArgoCD.

## What we have (see inventory/)

- **floor2 (T7910)** — 40 threads, 128GB, 9TB. Titan X working; **2× P40 24GB
  installed but thermally unusable** → these relocate.
- **Precision 7820 #1** — 2× Xeon Gold 5222 (8c/16t, 3.8GHz), bare (no RAM/SSD/GPU).
- **Tesla P40 24GB ×1** confirmed purchased + more P40s/GPUs in the $1,229 order.
- **Second tower, Kingwin open-air GPU rack, 2 motherboards, 2 PSUs, RAM, SSDs,
  fans, wiring harnesses** — arriving/arrived (Jul 1–2 orders in transit).

**Working GPU pool to allocate: 3–5× P40 (72–120GB VRAM) + Titan X 12GB.**

## The one fact that drives every option

P40s are passive server cards. They die (exactly as observed on floor2) without
ducted forced air. **Every P40, wherever it lands, needs either a $15–25 blower
kit or open-air + external fans.** That's the whole thermal fix.

---

## Option A — "Two Dell Workhorses" (max reliability)

Floor 3 = 7820 #1 with 2× P40 (blower kits). Floor 4 = tower #2 with P40 + Titan X
class cards. floor2 keeps orchestration only.

- **New spend:** ~$150–250 (4–5 blower kits $100, EPS adapters $30, RAM gap if the
  purchased RAM doesn't fit the 7820's DDR4-2933 RDIMM requirement ~$80/box)
- **Pros:** enterprise PSUs/airflow, ECC, quiet-ish, lowest assembly risk, 7820 GPU
  bays + 950W PSU handle 2× 250W cards properly.
- **Cons:** Kingwin rack + spare motherboards/PSUs sit unused; max 2 GPUs/box.

## Option B — "Kingwin Open-Air Inference Appliance" (max VRAM density)

All P40s (3–5) on the Kingwin rack, driven by one purchased motherboard + 2 PSUs
+ powered risers; box fans blowing across the cards. Pure inference node
(llama.cpp/Ollama row-split across cards). The 7820 becomes a CPU/dev node.

- **New spend:** ~$180–280 (powered x16 risers 4×$25, CPU+RAM for mystery board if
  not in the haul ~$60–100, blower kits optional in open air)
- **Pros:** best thermals possible, whole VRAM pool (up to ~120GB) on one host —
  70B q8 / 100B+ q4 territory; cheapest per-GB-VRAM.
- **Cons:** consumer-grade mystery boards, no ECC, dust/noise, riser jank, single
  point of failure, PCIe x1-x4 risers bottleneck multi-GPU tensor traffic.

## Option C — "Hybrid: 1 Workhorse + Open-Air Expansion" ⭐ RECOMMENDED

- **Floor 3 (production inference): 7820 #1** — RAM + NVMe/SATA SSDs from the
  haul, **2× P40 w/ blower kits + EPS harnesses** = 48GB VRAM. Runs 70B q4
  (~40GB) via Ollama; joins k3s as agent; n8n worker; PyTorch for LoRA jobs.
- **Floor 4 (batch/experimental): Kingwin open-air rig** — remaining P40(s) +
  other GPU cards, driven by tower #2 (preferred — real PSU, known board) or a
  purchased motherboard. Video gen, training runs, overflow inference.
- **floor2 (orchestration brain):** gives up its two P40s during one maintenance
  window, keeps Titan X (display/embeddings/small models), keeps k3s
  control-plane, n8n, Qdrant, ArgoCD.
- **New spend:** ~$130–200 · **Uses every purchased part** · P40s finally breathe.

| | A | B | C ⭐ |
|---|---|---|---|
| New $ | 150–250 | 180–280 | 130–200 |
| Usable VRAM | 72–96GB (split 2 boxes) | up to 120GB (1 box) | 96–120GB (2 boxes) |
| Reliability | ★★★ | ★ | ★★☆ |
| Uses Kingwin rack | no | yes | yes |
| Biggest model | 70B q4 | 70B q8+ | 70B q4 + batch box |

## Parts gap — 3 cost-effective sourcing solutions

| Gap | Budget fix | Mid fix | Premium fix |
|---|---|---|---|
| P40 cooling ×4–5 | eBay/Etsy 3D-printed shroud + dual 40mm blower, ~$16/card (~$80) | ARCTIC S4028-6K + printed duct ~$25/card | Water blocks — skip |
| P40 power (8-pin **EPS**, not PCIe!) | 2× PCIe-8pin→EPS adapter ~$9/card if harnesses in haul don't fit | Dell 7820 GPU power cable kit (0TP19V-class) ~$15 | — |
| 7820 RAM (DDR4 ECC **RDIMM**, 2933 for Gold 5222) | 4×16GB 2Rx4 2666 used ~$75/box | 8×16GB = 128GB ~$150 | 2933 native ~$220 |
| Kingwin risers | used powered x16 ribbon ×4 ~$90 | Thermaltake 600mm ~$45/ea | — |
| Mystery-board CPUs (Option B/C floor 4 only, if tower #2 short) | E5-2680 v4 pulls ~$15/ea | — | — |

**Order today (Option C): ~5 blower kits + 2 EPS adapters + 1 RAM kit ≈ $170.**

## P40 software notes (from floor2 experience + Pascal reality)

- Ollama/llama.cpp = first-class on Pascal (q4/q5/q8). **vLLM/flash-attention:
  poor/none on Pascal — don't plan around it.**
- FP16 is crippled (1:64) on P40 — PyTorch training in FP32 or int8 LoRA on ≤13B.
- Model plan: 1× P40 → qwen2.5:32b q4 (19GB) comfortably; 2× P40 → llama3.3/qwen
  70B q4; Titan X → nomic-embed + 7B utility models.
- Driver 535 series already proven on floor2 with Pascal + Maxwell mix.

## Move forward TODAY — parallel tracks

**Track A — Physical (Jimmer, ~2–4h)**
1. Maintenance window on floor2 (announce, `kubectl drain` optional): reboot,
   watch dmesg for P40 NVRM/Xid; confirm EPS vs PCIe plugs; **pull both P40s**.
2. Assemble 7820 #1: RAM + SSDs + 2× P40 (hold blower kits if not yet arrived —
   idle/light duty is safe at open side panel + house fan short-term).
3. Assemble Kingwin rack as parts arrive (Jul 1–2 shipments).

**Track B — Remote/software (Claude — started now)**
1. ✅ This repo (local + GitHub `expansion`), inventory + audit committed.
2. ✅ `scripts/bootstrap-floor.sh` — one-shot node build: NVIDIA driver, Ollama,
   PyTorch venv, k3s agent join, node labels; idempotent.
3. ✅ `scripts/p40-health.sh` — temp/throttle watchdog (n8n-friendly JSON output).
4. k3s join token + ArgoCD app-of-apps for new floors (gitops/, after floor 3 boots).

**Track C — Orders (today, ~$170)**
Blower kits ×5, EPS adapters ×2, 64GB RDIMM kit (verify haul RAM type first).

**Track D — Paper trail**
Pull eBay purchase-history line items for order `v2_f534cc54…` to finalize
inventory/purchases.md checklist.

## Success criteria

- Floor 3 answers `ollama run qwen2.5:32b` from the LAN and shows Ready in
  `kubectl get nodes` on floor2's cluster within 24h of parts landing.
- Both ex-floor2 P40s hold <80°C under sustained 70B inference with blower kits.
- floor2 load drops (no GPU inference) while n8n/ArgoCD/Qdrant stay green.
