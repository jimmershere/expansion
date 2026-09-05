#!/usr/bin/env python3
"""Turn photos/originals/ into web-ready responsive assets in photos/web/.

For each source image this writes progressive JPEG + WebP at several widths,
strips ALL metadata (EXIF, GPS, camera serials -- customer cars should not ship
with the location they were photographed at), honours EXIF orientation, and
emits photos/web/manifest.json for the site to consume.

    python3 scripts/optimize-photos.py            # incremental
    python3 scripts/optimize-photos.py --force    # rebuild everything

Naming convention for before/after pairs, which the manifest understands:

    1967-mustang--before.jpg
    1967-mustang--after.jpg
"""
import argparse, json, re, sys
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillow is required:  python3 -m pip install Pillow")

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "photos" / "originals"
OUT = ROOT / "photos" / "web"
WIDTHS = [480, 960, 1440, 1920]
JPEG_Q, WEBP_Q = 82, 80
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".heic"}


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return re.sub(r"-{2,}", "-", s) or "photo"


def variant_of(stem: str):
    """Split '1967-mustang--after' into ('1967-mustang', 'after')."""
    for tag in ("before", "after"):
        if stem.endswith(f"--{tag}"):
            return stem[: -len(tag) - 2], tag
    return stem, None


def process(path: Path, force: bool):
    # Detect the pair suffix on the RAW stem: slugify() collapses the '--'
    # separator, so it has to run after the split, not before.
    raw_base, variant = variant_of(path.stem.lower())
    base = slugify(raw_base)
    stem = f"{base}-{variant}" if variant else base
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im)          # respect camera rotation
        im = im.convert("RGB")                    # drop alpha/CMYK for JPEG
        w0, h0 = im.size
        widths = [w for w in WIDTHS if w < w0] + [w0]

        newest_src = path.stat().st_mtime
        sizes = []
        for w in widths:
            h = round(h0 * w / w0)
            resized = im.resize((w, h), Image.LANCZOS) if w != w0 else im
            entry = {"width": w, "height": h}
            for ext, kwargs in (
                ("jpg", dict(format="JPEG", quality=JPEG_Q, optimize=True, progressive=True)),
                ("webp", dict(format="WEBP", quality=WEBP_Q, method=6)),
            ):
                dest = OUT / f"{stem}-{w}w.{ext}"
                if force or not dest.exists() or dest.stat().st_mtime < newest_src:
                    resized.save(dest, **kwargs)   # no exif= kwarg -> metadata stripped
                entry[ext] = dest.name
            sizes.append(entry)

    return {
        "id": stem,
        "pair": base if variant else None,
        "variant": variant,
        "source": path.name,
        "alt": base.replace("-", " ").title() + (f" ({variant})" if variant else ""),
        "intrinsic": {"width": w0, "height": h0},
        "sizes": sizes,
        "srcset": {
            fmt: ", ".join(f"{s[fmt]} {s['width']}w" for s in sizes)
            for fmt in ("jpg", "webp")
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="rebuild even if up to date")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    srcs = sorted(p for p in SRC.rglob("*") if p.suffix.lower() in EXTS)
    if not srcs:
        sys.exit(f"no source images in {SRC} -- run scripts/fetch-fb-photos.sh first")

    entries, failed = [], []
    for p in srcs:
        try:
            entries.append(process(p, args.force))
            print(f"  ok   {p.name}")
        except Exception as e:                     # a corrupt download shouldn't kill the run
            failed.append((p.name, e))
            print(f"  FAIL {p.name}: {e}", file=sys.stderr)

    (OUT / "manifest.json").write_text(json.dumps(entries, indent=2) + "\n")
    print(f"\n{len(entries)} image(s) -> {OUT.relative_to(ROOT)}/manifest.json")
    if failed:
        print(f"{len(failed)} failed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
