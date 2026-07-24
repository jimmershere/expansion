from __future__ import annotations

import re
from typing import Optional

# canonical make -> aliases seen in listing titles
MAKES: dict[str, list[str]] = {
    "Chevrolet": ["chevrolet", "chevy", "chev"],
    "Ford": ["ford"],
    "Dodge": ["dodge"],
    "Ram": ["ram"],
    "GMC": ["gmc"],
    "Toyota": ["toyota"],
    "Nissan": ["nissan", "datsun"],
    "Honda": ["honda"],
    "Acura": ["acura"],
    "Mazda": ["mazda"],
    "Mitsubishi": ["mitsubishi", "mitsu"],
    "Subaru": ["subaru"],
    "Eagle": ["eagle"],
    "Plymouth": ["plymouth"],
    "Pontiac": ["pontiac"],
    "Oldsmobile": ["oldsmobile", "olds"],
    "Buick": ["buick"],
    "Cadillac": ["cadillac", "caddy"],
    "Chrysler": ["chrysler"],
    "Jeep": ["jeep"],
    "Volkswagen": ["volkswagen", "vw"],
    "Mercedes-Benz": ["mercedes-benz", "mercedes", "benz"],
    "BMW": ["bmw"],
    "Porsche": ["porsche"],
    "AMC": ["amc"],
    "International": ["international", "ih"],
    "Studebaker": ["studebaker"],
    "Lexus": ["lexus"],
    "Infiniti": ["infiniti"],
}

_ALIAS_TO_MAKE = {a: make for make, aliases in MAKES.items() for a in aliases}
_YEAR_RE = re.compile(r"\b(19[3-9]\d|20[0-2]\d)\b")
_MILEAGE_PATTERNS = [
    re.compile(r"[Dd]riven\s+([\d,]+)\s*miles"),          # FB detail page
    re.compile(r"\b([\d,]{4,7})\s*(?:original\s+)?miles\b", re.I),
    re.compile(r"\b(\d{1,3})\s*[kK]\s*(?:original\s+)?miles?\b"),
    re.compile(r"\bmileage[:\s]+([\d,]+)", re.I),
]


def parse_year(text: str) -> Optional[int]:
    m = _YEAR_RE.search(text)
    return int(m.group(1)) if m else None


def parse_make_model(title: str) -> tuple[str, str]:
    """'1972 Chevy C10 shortbed' -> ('Chevrolet', 'C10 shortbed')."""
    words = title.split()
    for i, w in enumerate(words):
        make = _ALIAS_TO_MAKE.get(w.lower().strip(".,"))
        if make:
            model_words = []
            for mw in words[i + 1 : i + 4]:
                if _YEAR_RE.fullmatch(mw) or mw.startswith("$"):
                    break
                model_words.append(mw.strip(".,"))
            return make, " ".join(model_words)
    return "", ""


def parse_mileage(text: str) -> Optional[int]:
    for pat in _MILEAGE_PATTERNS:
        m = pat.search(text)
        if not m:
            continue
        raw = m.group(1).replace(",", "")
        if not raw.isdigit():
            continue
        val = int(raw)
        if "k" in m.group(0).lower() and val < 1000:
            val *= 1000
        if 100 <= val <= 1_000_000:
            return val
    return None


def parse_price(text: str) -> Optional[int]:
    m = re.search(r"\$\s*([\d,]+)", text)
    if not m:
        return None
    val = int(m.group(1).replace(",", ""))
    return val if val > 0 else None


_VIN_RE = re.compile(r"\b([A-HJ-NPR-Z0-9]{17})\b")


def parse_vin(text: str) -> str:
    """17-char modern VINs only; pre-1981 VINs are free-form and skipped."""
    for m in _VIN_RE.finditer(text.upper()):
        vin = m.group(1)
        if any(c.isdigit() for c in vin) and any(c.isalpha() for c in vin):
            return vin
    return ""
