#!/usr/bin/env python3
"""Turn photos/originals/ into web-ready responsive assets in photos/web/.

For each source image this writes progressive JPEG + WebP at several widths,
strips ALL metadata (EXIF, GPS, camera serials -- customer cars should not ship
with the location they were photographed at), honours EXIF orientation, and
emits photos/web/manifest.json for the site to consume.

    python3 scripts/optimize-photos.py            # incremental
    python3 scripts/optimize-photos.py --force    # rebuild everything

iPhone .heic originals need a decoder stock Pillow does not ship:

    python3 -m pip install Pillow pillow-heif

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

# Stock Pillow cannot decode HEIC/HEIF, which is what iPhones shoot by default.
# Register the decoder when it is installed; when it is not, those files are
# left out of EXTS so they are reported up front instead of failing one by one.
try:
    import pillow_heif

    pillow_heif.register_heif_opener()
    HEIF_OK = True
except ImportError:
    HEIF_OK = False

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "photos" / "originals"
OUT = ROOT / "photos" / "web"
WIDTHS = [480, 960, 1440, 1920]
JPEG_Q, WEBP_Q = 82, 80
HEIF_EXTS = {".heic", ".heif"}
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"} | (HEIF_EXTS if HEIF_OK else set())


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return re.sub(r"-{2,}", "-", s) or "photo"


def variant_of(stem: str):
    """Split '1967-mustang--after' into ('1967-mustang', 'after')."""
    for tag in ("before", "after"):
        if stem.endswith(f"--{tag}"):
            return stem[: -len(tag) - 2], tag
    return stem, None


def name_for(path: Path):
    """Pair-group key, proposed base name, and pair variant for a source file.

    Sources are discovered recursively and a Meta page export arrives as album
    folders, so the basename alone is not unique -- album1/IMG_0001.jpg and
    album2/IMG_0001.jpg would collide and overwrite each other. Fold the
    folders into the name. Detect the pair suffix on the RAW stem first:
    slugify() collapses the '--' separator.

    The group key uses the real un-slugified path, so two folders that only
    differ in punctuation (album-1/ vs album_1/) are still distinct groups
    even though they propose the same base name.
    """
    rel = path.relative_to(SRC)
    raw_base, variant = variant_of(rel.stem.lower())
    parts = [slugify(p) for p in rel.parent.parts] + [slugify(raw_base)]
    return (rel.parent, raw_base), "-".join(p for p in parts if p), variant


def process(path: Path, stem: str, base: str, variant, force: bool):
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

    # Explicit <img src> fallback so templates never have to index into sizes[]:
    # a source 480px or narrower produces exactly one entry.
    fallback = next((s for s in reversed(sizes) if s["width"] <= 960), sizes[0])
    return {
        "id": stem,
        "pair": base if variant else None,
        "variant": variant,
        "source": str(path.relative_to(SRC)),
        "alt": base.replace("-", " ").title() + (f" ({variant})" if variant else ""),
        "intrinsic": {"width": w0, "height": h0},
        "fallback": fallback,
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

    if not HEIF_OK:
        skipped = [p for p in SRC.rglob("*") if p.suffix.lower() in HEIF_EXTS]
        if skipped:
            print(
                f"warning: skipping {len(skipped)} HEIC/HEIF file(s) -- stock Pillow "
                f"cannot decode them.\n         python3 -m pip install pillow-heif",
                file=sys.stderr,
            )

    if not srcs:
        sys.exit(f"no source images in {SRC} -- run scripts/fetch-fb-photos.sh first")

    entries, failed, taken = [], [], {}
    bases, used_bases = {}, {}
    for p in srcs:
        key, proposed, variant = name_for(p)
        if key not in bases:
            # Disambiguate at the GROUP level, not per file: a before/after set
            # shares one pair key, so suffixing each file separately would let
            # two albums share a pair key (or split one album's set across two).
            base, n = proposed, 2
            while base in used_bases:
                base, n = f"{proposed}-{n}", n + 1
            if base != proposed:
                print(f"  note {p.relative_to(SRC)} normalizes onto "
                      f"{used_bases[proposed].relative_to(SRC)}, keying it {base}")
            used_bases[base] = p
            bases[key] = base
        base = bases[key]

        stem = f"{base}-{variant}" if variant else base
        if stem in taken:                          # e.g. x--before.jpg vs x-before.jpg
            uniq, n = stem, 2
            while uniq in taken:
                uniq, n = f"{stem}-{n}", n + 1
            print(f"  note {p.relative_to(SRC)} collides with "
                  f"{taken[stem].relative_to(SRC)}, naming it {uniq}")
            stem = uniq
        taken[stem] = p
        try:
            entries.append(process(p, stem, base, variant, args.force))
            print(f"  ok   {p.relative_to(SRC)}")
        except Exception as e:                     # a corrupt download shouldn't kill the run
            failed.append((p.name, e))
            print(f"  FAIL {p.relative_to(SRC)}: {e}", file=sys.stderr)

    (OUT / "manifest.json").write_text(json.dumps(entries, indent=2) + "\n")
    print(f"\n{len(entries)} image(s) -> {OUT.relative_to(ROOT)}/manifest.json")
    if failed:
        print(f"{len(failed)} failed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
