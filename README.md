# expansion

Planning + automation repo for growing the home AI factory from one floor
(floor2, 192.168.1.206) to three: production inference, batch/experimental,
and orchestration — built from the Apr–Jul 2026 eBay hardware haul
(2× Dell Precision 7820-class towers, Tesla P40s, Kingwin open-air GPU rack,
RAM/SSDs/PSUs/fans/harnesses).

| File | What |
|---|---|
| [PROPOSAL.md](PROPOSAL.md) | 3 scoped build options, parts-gap pricing, recommended hybrid plan, parallel move-forward-today tracks |
| [inventory/purchases.md](inventory/purchases.md) | Purchase evidence from Gmail (PayPal/Klarna/Cash App) with checklist |
| [inventory/floor2-audit.md](inventory/floor2-audit.md) | Live audit of floor2 incl. the P40 thermal failure diagnosis |
| [scripts/bootstrap-floor.sh](scripts/bootstrap-floor.sh) | One-shot new-node build: NVIDIA 535, Ollama (LAN), PyTorch cu121, k3s agent join |
| [scripts/p40-health.sh](scripts/p40-health.sh) | GPU thermal/presence watchdog, JSON for n8n |
| gitops/ | ArgoCD app-of-apps for new floors (populated once floor3 joins) |
| [photos/](photos/README.md) | Appearance Unlimited restoration photos for appearance-unlimited.com + the fetch/optimize pipeline |
| [scripts/fetch-fb-photos.sh](scripts/fetch-fb-photos.sh) | Pulls the Appearance Unlimited Facebook page photos into `photos/originals/` |
| [scripts/optimize-photos.py](scripts/optimize-photos.py) | Responsive JPEG/WebP + manifest.json, strips EXIF/GPS |

## TL;DR

Both P40s in floor2 are dead-to-driver from passive-cooling thermal failure —
they enumerate on PCI but never initialize. The fix costs ~$16/card (blower
kits). Recommended: **Option C** — 7820 workhorse (2× P40, 48GB) as floor3 +
Kingwin open-air rig as floor4, floor2 stays the k3s/n8n/ArgoCD brain.
~$130–200 of gap parts total.
