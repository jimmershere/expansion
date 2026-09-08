# photos/

Auto restoration / detailing photos for the new **appearance-unlimited.com** site.

## Status

**Pulled 2026-09-08.** `scripts/fetch-fb-photos.sh --browser firefox` worked from
pop-os against <https://www.facebook.com/appearanceunlimited>: 424 photos
covering **2024-01-30 → 2026-08-11**, in `photos/fb-raw/` (untracked — see
below). The pull was stopped there by hand; it had not reached the end of the
album, and re-running the script resumes, because gallery-dl skips files it has
already written.

| Folder | What | Tracked |
|---|---|---|
| `fb-raw/` | The raw gallery-dl pull, `<photo-id>.jpg` + `.json` sidecar carrying the post date | no — gitignored |
| `originals/` | The 18 photos curated for the site, renamed per §2 below | not committed yet — rights check first |
| `web/` | Build output | no |

`fb-raw/` is gitignored on purpose: this repo is **public**, and those are
customer vehicles. Nothing here has been pushed. See *Rights* at the bottom
before committing or publishing any of it.

Two things the pull established that the site does not reflect:

* **The four named builds on the site have no photos in the archive.** No 1969
  Camaro SS (Northern Light), no 1966 C10 (Yellowjacket), no 1966 Mustang
  (Snowbird), no 1957 Bel Air (Resurrection). The yellow C10 currently on the
  site (`assets/img/Chevyc10.png`) is a stock photo, not a shop build.
* **There is a fully documented restoration the site does not mention** — an
  1980s Dodge D150 ("GRYFIN"), shot from as-delivered through teardown,
  bodywork, primer and paint to finished. It is the shop's best build story and
  it fits a build page's six-stage gallery exactly.

The archive is also body-shop heavy: essentially no detailing or paint-correction
photos, and no clean exterior shot of the building.

## 1. Get the photos

Best to worst source — Facebook re-encodes uploads and caps them around 2048px
on the long edge, which is fine for gallery thumbnails but thin for a
full-bleed hero image:

1. **The shop's own files.** Ask for the original camera/phone files. This is
   the only source with full resolution, and it costs one Dropbox link.
2. **Meta Business Suite export.** Business Suite → Settings → *Download page
   data* (or the page's *Download Your Information*) → select Posts/Photos.
   Meta emails a zip of the originals as uploaded. No scraping, no rate limits.
3. **Scrape the CDN copies** — the fallback:

   ```bash
   ./scripts/fetch-fb-photos.sh                    # Chrome cookies
   ./scripts/fetch-fb-photos.sh --browser firefox
   ./scripts/fetch-fb-photos.sh --cookies ./cookies.txt
   ```

   Requires being logged into Facebook as someone with access to the page —
   Facebook does not serve page photo albums to logged-out visitors.

Drop whatever you get into `originals/`.

## 2. Name them

The build understands before/after pairs via a `--before` / `--after` suffix,
which is most of what a restoration gallery is:

```
originals/1967-mustang-fastback--before.jpg
originals/1967-mustang-fastback--after.jpg
originals/shop-front.jpg
```

The part before `--` becomes the pair key and the alt text, so name it like a
customer would describe the car, not `IMG_4821`.

## 3. Build the web assets

```bash
python3 -m pip install Pillow pillow-heif
python3 scripts/optimize-photos.py          # incremental
python3 scripts/optimize-photos.py --force  # rebuild all
```

Per image this emits progressive JPEG + WebP at 480/960/1440/1920px (never
upscaled past the original), and writes `web/manifest.json` with dimensions,
alt text, pair keys, ready-made `srcset` strings, and a `fallback` entry to use
as the plain `<img src>`. Use `fallback` rather than indexing into `sizes` —
a source 480px or narrower yields only one size, so `sizes[1]` would not exist.

`pillow-heif` is what decodes iPhone `.heic` originals; without it the script
says so and skips them. Sub-folders are folded into the output name, so a Meta
export's album folders keep otherwise identical `IMG_0001.jpg` basenames
apart.

It also **strips all metadata**. Customer cars get photographed in the shop and
in driveways; the EXIF carries GPS coordinates and camera serials that should
not ship to a public website. Orientation is applied to the pixels first so
phone photos don't come out sideways.

### Using the manifest

```html
<picture>
  <source type="image/webp" srcset="{{ srcset.webp }}" sizes="(max-width: 700px) 100vw, 700px">
  <img src="{{ fallback.jpg }}" srcset="{{ srcset.jpg }}"
       width="{{ intrinsic.width }}" height="{{ intrinsic.height }}"
       alt="{{ alt }}" loading="lazy" decoding="async">
</picture>
```

Always emit `width`/`height` — it reserves layout space and keeps the page's
CLS score at zero. Use `loading="eager"` plus `fetchpriority="high"` on the one
hero image, `lazy` on everything else.

## Rights

These are the customer's photos of customer vehicles. Before publishing:
confirm Appearance Unlimited owns or has permission for each shot (photos taken
by a third-party photographer are that photographer's copyright), and avoid
publishing readable license plates or faces without an OK.
