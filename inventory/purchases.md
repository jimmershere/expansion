# Purchase Evidence — Hardware Expansion (Apr 30 – Jul 2, 2026)

Compiled 2026-07-04 from Gmail (PayPal, Klarna, Cash App receipts) and openclaw
workspace notes from the purchase week.

## Confirmed, itemized

| Date | Channel | Item | Amount |
|---|---|---|---|
| 2026-04-30 | eBay via PayPal (Visa ••7295) | Multi-item eBay checkout — order `v2_f534cc54…`, txn `9Y564067PR7068140`. Not itemized in receipt; per May 3 workspace notes this is the "parts + 24GB GPU, 2 more servers incoming" order (second tower, additional P40s/GPU cards, Kingwin open-air rack, RAM/motherboards/PSUs candidates) | $1,229.35 |
| 2026-05-03 | eBay via Klarna (pay-in-4, $107.00×4, completed 6/27) | **Dell Precision 7820 tower, 2× Xeon Gold 5222 3.80 GHz — no RAM, no SSD, no GPU, 4× SATA** + $28 delivery | $427.99 |
| 2026-05-03 | eBay via Klarna (pay-in-4, completed 6/26) | **NVIDIA Tesla P40 24GB GDDR5 PCIe 3.0 x16, 1yr warranty** + $20.65 delivery | $315.64 |
| 2026-05-11 | eBay via Cash App | small part (unitemized) | $45.70 |
| 2026-07-01 | eBay via Cash App | small part (unitemized) — fans / wiring harness class | $55.11 |
| 2026-07-01 | eBay via Cash App | small part (unitemized) | $40.63 |
| 2026-07-01 | eBay via Cash App | small part (unitemized) | $43.59 |
| 2026-07-02 | eBay via Cash App | part (unitemized, pending) — RAM / PSU / rack class | $147.27 |

**eBay hardware total ≈ $2,305.** The Jul 1–2 orders are in transit now.

Possibly related: 2× Lowes PayPal charges on May 3 ($412.52, $212.93) — timing
matches build week (electrical/wiring supplies?), unconfirmed.

## Owner's stated haul (target checklist)

- [x] Dell Precision tower #1 (7820, 2× Gold 5222) — Klarna receipt
- [ ] Dell Precision tower #2 — inside Apr 30 order (confirm on arrival)
- [x] Tesla P40 24GB ×1 — Klarna receipt
- [ ] Additional Tesla P40s + other GPU cards — inside Apr 30 order
- [ ] Kingwin open-air GPU rack — inside Apr 30 order
- [ ] RAM, 2× motherboards, several SSDs, 2× PSUs — inside Apr 30 / Cash App orders
- [ ] Wiring harnesses, fans — Cash App Jul 1 orders (in transit)

> The eBay itemized order-confirmation emails do not land in jimmershere@gmail.com
> (only payment-processor receipts do). Action: pull the eBay purchase-history page
> for order `v2_f534cc54-665b-464e-b8ca-69d8a565c6ca` to lock down exact line items.

## Already deployed at floor2 (prior purchases)

- 2× Tesla P40 24GB — physically installed in floor2's T7910, **failing to
  initialize** (see floor2-audit.md)
- GTX Titan X 12GB (Maxwell) — working
