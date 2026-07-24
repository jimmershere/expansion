from __future__ import annotations

import json
import sqlite3
import statistics
import time
from typing import Optional

from mscout.fb import FBMarketplace
from mscout.models import Listing
from mscout.normalize import parse_year


class CompsEngine:
    """Average northern-US resale value = trimmed median of comparable
    Marketplace asking prices across the configured northern metros.

    Medians are cached (sqlite) per make/model/year-bucket so a sweep with
    twenty '72 C10s researches the value once, not twenty times. Asking
    prices run a few percent above true sale prices — treat the number as a
    ceiling, which is fine when hunting for below-market ads.
    """

    def __init__(self, cfg: dict, fb: Optional[FBMarketplace]):
        self.cfg = cfg
        self.fb = fb
        self.db = sqlite3.connect(cfg["paths"]["cache_db"])
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS comps ("
            " key TEXT PRIMARY KEY, median INTEGER, n INTEGER,"
            " prices TEXT, fetched_at REAL)"
        )
        self.db.commit()

    def value(self, listing: Listing) -> None:
        f = self.cfg["filters"]
        if not listing.make or not listing.year:
            listing.notes.append("no comps: could not normalize make/year")
            return

        key = listing.comp_key(f["comp_year_window"])
        cached = self._get_cached(key)
        if cached:
            listing.avg_resale_north, listing.comp_count = cached
            return

        prices = self._gather_comp_prices(listing)
        if len(prices) < f["min_comps"]:
            listing.notes.append(f"no comps: only {len(prices)} found (need {f['min_comps']})")
            return

        median = self._trimmed_median(prices, f["comp_trim_pct"])
        listing.avg_resale_north = median
        listing.comp_count = len(prices)
        self.db.execute(
            "INSERT OR REPLACE INTO comps VALUES (?,?,?,?,?)",
            (key, median, len(prices), json.dumps(prices), time.time()),
        )
        self.db.commit()

    # -- internals ---------------------------------------------------------
    def _get_cached(self, key: str) -> Optional[tuple[int, int]]:
        ttl = self.cfg["comp_cache_ttl_days"] * 86400
        row = self.db.execute(
            "SELECT median, n, fetched_at FROM comps WHERE key=?", (key,)
        ).fetchone()
        if row and time.time() - row[2] < ttl:
            return int(row[0]), int(row[1])
        return None

    def _gather_comp_prices(self, listing: Listing) -> list[int]:
        if self.fb is None:
            return []
        f = self.cfg["filters"]
        w = f["comp_year_window"]
        query = f"{listing.year} {listing.make} {listing.model}".strip()
        prices: list[int] = []
        for metro in self.cfg["comp_metros"]:
            try:
                for comp in self.fb.search(
                    metro, query,
                    min_year=listing.year - w, max_year=listing.year + w,
                ):
                    if comp.asking_price and self._plausible(comp, listing):
                        prices.append(comp.asking_price)
            except Exception as e:  # one metro failing shouldn't kill the run
                listing.notes.append(f"comps: {metro} failed ({type(e).__name__})")
            # enough signal? stop burning page loads
            if len(prices) >= 4 * f["min_comps"]:
                break
        return prices

    def _plausible(self, comp: Listing, target: Listing) -> bool:
        """Comp must mention the model and sit in the year window."""
        f = self.cfg["filters"]
        title = comp.title.lower()
        model_head = target.model.split()[0].lower() if target.model else ""
        if model_head and model_head not in title:
            return False
        y = parse_year(comp.title)
        if y and target.year and abs(y - target.year) > f["comp_year_window"]:
            return False
        p = comp.asking_price or 0
        return f["min_price"] <= p <= f["max_price"]

    @staticmethod
    def _trimmed_median(prices: list[int], trim_pct: int) -> int:
        s = sorted(prices)
        k = int(len(s) * trim_pct / 100)
        trimmed = s[k : len(s) - k] if len(s) > 2 * k else s
        return int(statistics.median(trimmed))
