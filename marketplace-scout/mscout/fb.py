from __future__ import annotations

import random
import re
import time
import urllib.parse
from typing import Iterator

from playwright.sync_api import BrowserContext, Page, sync_playwright

from mscout.models import Listing
from mscout.normalize import parse_mileage, parse_price, parse_vin

# All Facebook-specific selectors/regexes live in this file. When Facebook
# changes markup and a run returns 0 cards, patch here.
ITEM_LINK_SEL = 'a[href*="/marketplace/item/"]'
_ITEM_ID_RE = re.compile(r"/marketplace/item/(\d+)")
_LOGIN_MARKERS = ("login", "checkpoint", "recover")


class FBMarketplace:
    """Drives a persistent, user-logged-in Chromium profile.

    Facebook has no public Marketplace API; this automates your own session,
    politely: random delays, scroll caps, and hard limits on detail fetches.
    """

    def __init__(self, cfg: dict):
        self.cfg = cfg
        self._pw = None
        self._ctx: BrowserContext | None = None
        self._detail_fetches = 0

    # -- lifecycle ---------------------------------------------------------
    def __enter__(self) -> "FBMarketplace":
        self._pw = sync_playwright().start()
        self._ctx = self._pw.chromium.launch_persistent_context(
            self.cfg["paths"]["profile_dir"],
            headless=self.cfg["pacing"]["headless"],
            viewport={"width": 1400, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
        )
        return self

    def __exit__(self, *exc) -> None:
        if self._ctx:
            self._ctx.close()
        if self._pw:
            self._pw.stop()

    def _sleep(self) -> None:
        p = self.cfg["pacing"]
        time.sleep(random.uniform(p["min_delay_s"], p["max_delay_s"]))

    def _page(self) -> Page:
        assert self._ctx is not None
        return self._ctx.pages[0] if self._ctx.pages else self._ctx.new_page()

    # -- login -------------------------------------------------------------
    def interactive_login(self) -> None:
        """Open facebook.com and wait for the human to finish logging in."""
        page = self._page()
        page.goto("https://www.facebook.com/")
        print("Log into Facebook in the browser window, then press Enter here...")
        input()
        page.goto("https://www.facebook.com/marketplace/")
        if self.logged_in(page):
            print("Login saved to profile — future runs can be headless.")
        else:
            print("Still not logged in; run `python -m mscout login` again.")

    def logged_in(self, page: Page) -> bool:
        return not any(m in page.url for m in _LOGIN_MARKERS)

    # -- search ------------------------------------------------------------
    def search(self, city: str, query: str, min_year: int | None = None,
               max_year: int | None = None) -> Iterator[Listing]:
        """Yield Listing stubs (url/title/price/location) from one search."""
        params = {"query": query, "exact": "false", "sortBy": "creation_time_descend"}
        if min_year:
            params["minYear"] = str(min_year)
        if max_year:
            params["maxYear"] = str(max_year)
        f = self.cfg["filters"]
        params["minPrice"] = str(f["min_price"])
        params["maxPrice"] = str(f["max_price"])
        url = (f"https://www.facebook.com/marketplace/{city}/search?"
               + urllib.parse.urlencode(params))

        page = self._page()
        page.goto(url, wait_until="domcontentloaded")
        self._sleep()
        if not self.logged_in(page):
            raise RuntimeError("Not logged in — run `python -m mscout login` first")

        seen: set[str] = set()
        cap = self.cfg["pacing"]["max_cards_per_search"]
        stagnant_scrolls = 0
        while len(seen) < cap and stagnant_scrolls < 3:
            before = len(seen)
            for card in page.query_selector_all(ITEM_LINK_SEL):
                href = card.get_attribute("href") or ""
                m = _ITEM_ID_RE.search(href)
                if not m or m.group(1) in seen:
                    continue
                seen.add(m.group(1))
                yield self._card_to_listing(card, m.group(1))
                if len(seen) >= cap:
                    break
            stagnant_scrolls = stagnant_scrolls + 1 if len(seen) == before else 0
            page.mouse.wheel(0, random.randint(1800, 2600))
            self._sleep()

    @staticmethod
    def _card_to_listing(card, item_id: str) -> Listing:
        # Card text is newline-separated: price / title / location / (mileage)
        lines = [ln.strip() for ln in (card.inner_text() or "").split("\n") if ln.strip()]
        price = next((parse_price(ln) for ln in lines if parse_price(ln)), None)
        title = next((ln for ln in lines if not ln.startswith("$") and len(ln) > 8), "")
        location = next((ln for ln in lines
                         if re.search(r",\s*[A-Z]{2}$", ln)), "")
        mileage = next((parse_mileage(ln) for ln in lines if parse_mileage(ln)), None)
        return Listing(
            url=f"https://www.facebook.com/marketplace/item/{item_id}/",
            title=title, asking_price=price, location=location, mileage=mileage,
        )

    # -- detail ------------------------------------------------------------
    def fetch_detail(self, listing: Listing) -> None:
        """Open the listing page; fill mileage, description, VIN."""
        if self._detail_fetches >= self.cfg["pacing"]["max_detail_pages"]:
            listing.notes.append("detail fetch skipped (run cap reached)")
            return
        self._detail_fetches += 1

        page = self._page()
        page.goto(listing.url, wait_until="domcontentloaded")
        self._sleep()
        try:  # expand truncated descriptions
            more = page.query_selector('span:has-text("See more")')
            if more:
                more.click()
                time.sleep(0.8)
        except Exception:
            pass

        body = page.inner_text("body")
        listing.description = body[:8000]
        if listing.mileage is None:
            listing.mileage = parse_mileage(body)
        if listing.asking_price is None:
            listing.asking_price = parse_price(body)
        listing.vin = parse_vin(body)
