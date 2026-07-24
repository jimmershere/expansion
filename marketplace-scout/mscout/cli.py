from __future__ import annotations

import argparse
import sys

from mscout.carfax import passes_blocklist, score_carfax
from mscout.config import load_config
from mscout.export_xlsx import write_xlsx
from mscout.models import Listing
from mscout.normalize import parse_make_model, parse_year


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(
        prog="mscout",
        description="Find under-priced classics/tuners on Facebook Marketplace",
    )
    ap.add_argument("--config", default=None, help="path to config.yaml")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("login", help="open a browser to log into Facebook once")

    run = sub.add_parser("run", help="sweep areas, value hits, export spreadsheet")
    run.add_argument("--areas", nargs="*", help="city slugs (default: config nc list)")
    run.add_argument("--categories", nargs="*", help="subset of config categories")
    run.add_argument("--threshold", type=float, help="override deal_threshold_pct")
    run.add_argument("--all-listings", action="store_true",
                     help="export everything found, not just deals")
    run.add_argument("--out", default="deals.xlsx")
    run.add_argument("--sheets", metavar="TITLE",
                     help="also push results to this Google Sheet")

    val = sub.add_parser("value", help="comp-value one vehicle, e.g.: value 1994 toyota supra")
    val.add_argument("words", nargs="+")

    demo = sub.add_parser("demo", help="write a sample spreadsheet (no Facebook needed)")
    demo.add_argument("--out", default="examples/demo-deals.xlsx")

    args = ap.parse_args(argv)
    cfg = load_config(args.config)

    if args.cmd == "demo":
        from mscout.demo_data import demo_listings
        listings = demo_listings()
        write_xlsx(listings, args.out, cfg["filters"]["deal_threshold_pct"])
        print(f"Wrote {len(listings)} SAMPLE rows to {args.out}")
        return

    from mscout.fb import FBMarketplace  # playwright import deferred off demo path
    from mscout.valuation import CompsEngine

    if args.cmd == "login":
        with FBMarketplace(cfg) as fb:
            fb.interactive_login()
        return

    if args.cmd == "value":
        text = " ".join(args.words)
        stub = Listing(url="", title=text)
        stub.year = parse_year(text)
        stub.make, stub.model = parse_make_model(text)
        with FBMarketplace(cfg) as fb:
            CompsEngine(cfg, fb).value(stub)
        if stub.avg_resale_north:
            print(f"{text}: ~${stub.avg_resale_north:,} "
                  f"(median of {stub.comp_count} northern-metro comps)")
        else:
            print(f"{text}: no value — {'; '.join(stub.notes)}")
        return

    # -- run ---------------------------------------------------------------
    if args.threshold is not None:
        cfg["filters"]["deal_threshold_pct"] = args.threshold
    areas = args.areas or [c for cities in cfg["search_areas"].values() for c in cities]
    cat_names = args.categories or list(cfg["categories"])
    unknown = set(cat_names) - set(cfg["categories"])
    if unknown:
        sys.exit(f"unknown categories: {', '.join(unknown)}")

    with FBMarketplace(cfg) as fb:
        found = _sweep(fb, cfg, areas, cat_names)
        print(f"\nFound {len(found)} unique listings; fetching details + valuing...")
        engine = CompsEngine(cfg, fb)
        for l in found:
            fb.fetch_detail(l)
            score_carfax(l)
            engine.value(l)

    threshold = cfg["filters"]["deal_threshold_pct"]
    deals = [l for l in found if (l.below_market_pct or 0) >= threshold]
    out_rows = found if args.all_listings else deals
    write_xlsx(out_rows, args.out, threshold)
    print(f"{len(deals)} deals ≥{threshold}% below northern-US comp median "
          f"→ {args.out} ({len(out_rows)} rows)")

    if args.sheets:
        from mscout.sheets import push_to_sheets
        url = push_to_sheets(out_rows, args.sheets, cfg)
        print(f"Google Sheet updated: {url}")


def _sweep(fb, cfg, areas: list[str], cat_names: list[str]) -> list[Listing]:
    f = cfg["filters"]
    by_url: dict[str, Listing] = {}
    for cat in cat_names:
        spec = cfg["categories"][cat]
        for area in areas:
            for query in spec["queries"]:
                print(f"  [{cat}] {area}: '{query}'")
                try:
                    hits = fb.search(area, query,
                                     min_year=spec.get("min_year"),
                                     max_year=spec.get("max_year"))
                    for l in hits:
                        if l.url in by_url:
                            continue
                        if passes_blocklist(l.title, f["blocked_keywords"]):
                            continue
                        l.category = cat
                        l.year = l.year or parse_year(l.title)
                        l.make, l.model = parse_make_model(l.title)
                        if _year_ok(l, spec) and _basics_ok(l, f):
                            by_url[l.url] = l
                except RuntimeError:
                    raise  # not logged in — stop the whole run
                except Exception as e:
                    print(f"    search failed: {type(e).__name__}: {e}")
    return list(by_url.values())


def _year_ok(l: Listing, spec: dict) -> bool:
    if l.year is None:
        return True  # keep; detail page may reveal it
    if spec.get("min_year") and l.year < spec["min_year"]:
        return False
    if spec.get("max_year") and l.year > spec["max_year"]:
        return False
    return True


def _basics_ok(l: Listing, f: dict) -> bool:
    if l.asking_price is not None and not (f["min_price"] <= l.asking_price <= f["max_price"]):
        return False
    if l.mileage is not None and l.mileage > f["max_mileage"]:
        return False
    return True
