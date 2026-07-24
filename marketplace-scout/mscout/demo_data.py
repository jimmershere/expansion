"""Sample listings so `mscout demo` can produce the spreadsheet format
without Facebook access. Prices/URLs are ILLUSTRATIVE, not live ads.
"""
from __future__ import annotations

from mscout.carfax import score_carfax
from mscout.models import Listing


def _mk(url_id, title, price, loc, cat, year, make, model, miles, desc,
        avg, comps) -> Listing:
    l = Listing(
        url=f"https://www.facebook.com/marketplace/item/{url_id}/",
        title=title, asking_price=price, location=loc, category=cat,
        year=year, make=make, model=model, mileage=miles, description=desc,
        avg_resale_north=avg, comp_count=comps,
    )
    score_carfax(l)
    return l


def demo_listings() -> list[Listing]:
    return [
        _mk("7412009315550001", "1972 Chevrolet C10 shortbed", 9500,
            "Raleigh, NC", "pickup_trucks", 1972, "Chevrolet", "C10", 78000,
            "Frame-off resto 10 yrs ago. Clean title in hand. 350/TH350.",
            14200, 23),
        _mk("7412009315550002", "1994 Toyota Supra MK4 targa", 38900,
            "Charlotte, NC", "import_tuners_90s", 1994, "Toyota", "Supra", 128000,
            "NA-T build, clean carfax, no accidents. VIN JT2JA82J0R0021476.",
            52000, 17),
        _mk("7412009315550003", "1993 Mazda RX-7 FD", 21500,
            "Greensboro, NC", "import_tuners_90s", 1993, "Mazda", "RX-7", 89000,
            "Rebuilt title from minor front hit in 2015. Fresh 13B rebuild.",
            29800, 14),
        _mk("7412009315550004", "1987 Ford F150 4x4", 6800,
            "Asheville, NC", "pickup_trucks", 1987, "Ford", "F150", 143000,
            "One owner, barn kept. Clean title.", 9100, 31),
        _mk("7412009315550005", "1969 Chevrolet Chevelle SS clone", 24000,
            "Fayetteville, NC", "classic_cars", 1969, "Chevrolet", "Chevelle", 52000,
            "396 big block, 12-bolt. Clear title.", 31500, 19),
        _mk("7412009315550006", "1991 Nissan 240SX coupe", 7200,
            "Wilmington, NC", "import_tuners_90s", 1991, "Nissan", "240SX", 161000,
            "SR20DET swap, tucked bay. No accidents.", 11800, 22),
        _mk("7412009315550007", "1978 Datsun 280Z restomod", 17500,
            "Raleigh, NC", "custom_vehicles", 1978, "Nissan", "280Z", 96000,
            "LS3 swap, T56, coilovers. Clean carfax equivalent — clear title.",
            24500, 11),
        _mk("7412009315550008", "1996 Mitsubishi Eclipse GSX", 8900,
            "Charlotte, NC", "import_tuners_90s", 1996, "Mitsubishi", "Eclipse GSX",
            118000, "AWD turbo, timing done. Odometer discrepancy noted on title.",
            12600, 9),
    ]
