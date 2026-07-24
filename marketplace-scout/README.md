# marketplace-scout

Finds under-priced classic pickups, classic cars, 90s import tuners, and custom
vehicles on Facebook Marketplace in chosen areas (default: North Carolina),
researches an average resale value for each hit from comparable listings in
northern-US metros, and exports a spreadsheet (`.xlsx`, optionally pushed to
Google Sheets) with:

`Make · Model · Year · Mileage · Clean Carfax (binary) · URL · Avg Resale Price (Northern US)`

plus asking price, $/% below market, location, category, and notes — sorted by
biggest discount first.

## How it works

```
search areas (NC cities) ──▶ FB Marketplace search (Playwright, your login)
                                    │  listing cards + detail pages
                                    ▼
                             normalize (year/make/model/mileage)
                                    │
              ┌─────────────────────┼──────────────────────┐
              ▼                     ▼                      ▼
      Carfax/title heuristics   comps engine          dedupe/filters
      (clean-carfax claims,     (same make/model,     (price floor to skip
       salvage/rebuilt/flood     year ±window, in      scam bait, mileage
       keywords in listing)      northern metros →     caps, keyword blocks)
                                 trimmed median)
              └─────────────────────┼──────────────────────┘
                                    ▼
                    deals = asking ≤ (1 - threshold) × comp median
                                    ▼
                       deals.xlsx  /  Google Sheet
```

## Setup

```bash
cd marketplace-scout
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# one-time: log into Facebook in the tool's dedicated browser profile
python -m mscout login
```

## Run

```bash
# full sweep: all categories, NC areas, comps from northern metros
python -m mscout run --out deals.xlsx

# just 90s tuners in Raleigh/Charlotte, at least 20% below market
python -m mscout run --categories import_tuners_90s --areas raleigh charlotte \
    --threshold 20 --out tuners.xlsx

# value one vehicle without a sweep
python -m mscout value 1994 toyota supra

# generate a sample spreadsheet (no Facebook access needed) to see the format
python -m mscout demo --out examples/demo-deals.xlsx

# push results to Google Sheets too (needs a service-account JSON, see below)
python -m mscout run --out deals.xlsx --sheets "NC Car Deals"
```

Everything (areas, comp metros, category search queries, thresholds, rate
limits) is configured in [`config.yaml`](config.yaml).

## Google Sheets upload

1. Create a Google Cloud service account, enable the Sheets + Drive APIs,
   download the JSON key to `~/.mscout/gcp-service-account.json`.
2. Share the target spreadsheet (or let the tool create one) with the service
   account's email.
3. Add `--sheets "<spreadsheet title>"` to `run`. Without credentials the tool
   still writes the `.xlsx`, which imports cleanly into Google Sheets
   (File → Import).

## Honest limitations

- **Facebook ToS / blocking.** There is no public Marketplace API. This tool
  automates *your own logged-in session* through a real browser, with random
  2–6 s delays and page caps. Keep runs modest (the defaults are) — hammering
  it can get the account checkpointed. Use at your own risk.
- **Selectors rot.** Facebook changes markup constantly. All DOM selectors and
  regexes live in `mscout/fb.py`; if a run suddenly returns 0 cards, that's
  the file to patch.
- **Clean Carfax is inferred, not verified.** `1` = seller explicitly claims a
  clean Carfax/AutoCheck or clean title and no branded-title keywords appear;
  `0` = salvage/rebuilt/flood/branded/rollback keywords found; blank = no
  evidence either way. A real report needs the VIN + a Carfax account — the
  tool extracts VINs into the Notes column when sellers post them so you can
  pull the report before buying.
- **"Average resale" = comp median, not KBB.** Book values barely exist for
  30-year-old and modified vehicles. The comps engine's trimmed median of live
  northern-metro asking prices is a good proxy but is still *asking*, not
  *sold*, prices — expect it to run a few percent above true sale value.
