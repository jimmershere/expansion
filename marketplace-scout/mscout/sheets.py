from __future__ import annotations

import os

from mscout.export_xlsx import COLUMNS
from mscout.models import Listing


def push_to_sheets(listings: list[Listing], spreadsheet_title: str, cfg: dict) -> str:
    """Upload results to a Google Sheet via a service account. Returns URL.

    Requires `pip install gspread` and a service-account JSON at
    paths.gcp_service_account (share the sheet with that account's email,
    or let this create it and share it back to you).
    """
    import gspread  # optional dep, imported lazily

    sa_path = cfg["paths"]["gcp_service_account"]
    if not os.path.exists(sa_path):
        raise FileNotFoundError(
            f"No service-account JSON at {sa_path} — see README 'Google Sheets upload'"
        )
    gc = gspread.service_account(filename=sa_path)
    try:
        sh = gc.open(spreadsheet_title)
    except gspread.SpreadsheetNotFound:
        sh = gc.create(spreadsheet_title)

    ws = sh.sheet1
    ws.clear()
    header = [c[0] for c in COLUMNS]
    rows = []
    for l in sorted(listings, key=lambda x: -(x.below_market_pct or -999)):
        notes = "; ".join([l.title_notes] + l.notes) if (l.title_notes or l.notes) else ""
        rows.append([
            l.make or "?", l.model or l.title[:28], l.year or "", l.mileage or "",
            "" if l.clean_carfax is None else l.clean_carfax, l.url,
            l.avg_resale_north or "", l.asking_price or "", l.below_market or "",
            l.below_market_pct or "", l.location, l.category, l.comp_count or "",
            notes,
        ])
    ws.update([header] + rows)
    ws.format("A1:N1", {"textFormat": {"bold": True}})
    return sh.url
