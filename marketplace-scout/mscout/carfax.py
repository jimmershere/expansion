from __future__ import annotations

import re
from typing import Optional

from mscout.models import Listing

# Evidence the history is BAD — any hit forces 0 regardless of clean claims.
_DIRTY = [
    r"salvage",
    r"rebuilt\s+title",
    r"rebuild\s+title",
    r"branded\s+title",
    r"flood",
    r"lemon\s+law",
    r"odometer\s+(?:rollback|discrepancy|exempt)",
    r"true\s+miles\s+unknown",
    r"tmu\b",
    r"frame\s+damage",
    r"theft\s+recovery",
    r"r\s*title",
]

# Evidence the seller affirmatively claims clean history.
_CLEAN = [
    r"clean\s+carfax",
    r"clean\s+car\s*fax",
    r"clean\s+autocheck",
    r"clean\s+title",
    r"clear\s+title",
    r"no\s+accidents?",
    r"accident[-\s]free",
    r"one\s+owner",
]

_DIRTY_RE = re.compile("|".join(_DIRTY), re.I)
_CLEAN_RE = re.compile("|".join(_CLEAN), re.I)


def score_carfax(listing: Listing) -> None:
    """Set listing.clean_carfax to 1/0/None from title+description evidence.

    This is a heuristic on seller claims, NOT a real Carfax pull — verify with
    the VIN before money changes hands.
    """
    text = f"{listing.title}\n{listing.description}"
    dirty = _DIRTY_RE.search(text)
    clean = _CLEAN_RE.search(text)

    if dirty:
        listing.clean_carfax = 0
        listing.title_notes = f"flag: '{dirty.group(0).strip()}'"
    elif clean:
        listing.clean_carfax = 1
        listing.title_notes = f"seller claims: '{clean.group(0).strip()}'"
    else:
        listing.clean_carfax = None
        listing.title_notes = "no history evidence in ad"

    if listing.vin:
        listing.notes.append(f"VIN {listing.vin} — pull real Carfax before buying")


def passes_blocklist(text: str, blocked: list[str]) -> Optional[str]:
    """Return the blocked keyword hit, or None if the text is fine."""
    low = text.lower()
    for kw in blocked:
        if kw.strip("*").lower() in low:
            return kw
    return None
