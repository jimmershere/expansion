from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Listing:
    """One Marketplace vehicle ad, progressively enriched by the pipeline."""

    url: str
    title: str = ""
    asking_price: Optional[int] = None
    location: str = ""
    category: str = ""

    # filled by normalize
    year: Optional[int] = None
    make: str = ""
    model: str = ""
    mileage: Optional[int] = None

    # filled by detail fetch
    description: str = ""
    vin: str = ""

    # filled by carfax heuristics: 1 clean, 0 branded/dirty, None unknown
    clean_carfax: Optional[int] = None
    title_notes: str = ""

    # filled by valuation
    avg_resale_north: Optional[int] = None
    comp_count: int = 0

    notes: list[str] = field(default_factory=list)

    @property
    def below_market(self) -> Optional[int]:
        if self.asking_price is None or self.avg_resale_north is None:
            return None
        return self.avg_resale_north - self.asking_price

    @property
    def below_market_pct(self) -> Optional[float]:
        if self.below_market is None or not self.avg_resale_north:
            return None
        return round(100.0 * self.below_market / self.avg_resale_north, 1)

    def comp_key(self, year_window: int) -> str:
        """Cache key for comps: make/model/year-bucket."""
        bucket = (self.year // year_window) * year_window if self.year else 0
        return f"{self.make.lower()}|{self.model.lower()}|{bucket}~{year_window}"
