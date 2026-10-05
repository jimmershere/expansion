# Site update package — 18 filled image frames

Everything needed to put the photos onto appearance-unlimited.com, in two
pieces so the images (which never conflict) are separate from the markup (which
might).

| File | What | Conflicts? |
|---|---|---|
| `assets-img-photos.tar.gz` | 166 built files — responsive JPEG + WebP at 480/960/1440/1920/native for all 18 photos. Extracts to `assets/img/photos/`. | No — pure addition |
| `site-markup.patch` | The HTML and CSS edits: 18 `.ph` frames swapped for `<picture>`, plus 3 CSS rules. | **Maybe — read below** |

## The conflict risk

The patch was generated against a **mirror of the live site as deployed
2026-09-08**, not against `/app/AU2` on quasimodo. This session never had SSH to
quasimodo, so the two have never been compared. If the AU2 draft has moved on
from what is deployed, the patch hunks will not apply cleanly.

The image tarball is safe regardless.

## Applying it on quasimodo

```bash
cd /app/AU2                      # or wherever the site tree actually is
git status                       # commit or stash anything in flight first

tar -xzf site-update/assets-img-photos.tar.gz     # -> assets/img/photos/
git apply --check site-update/site-markup.patch   # dry run, prints conflicts
git apply site-update/site-markup.patch
```

If `--check` complains, the frames are easy to place by hand — each one is the
same shape. Find the placeholder:

```html
<div class="ph ph-4x3"><span class="ph-label">Custom paint — spray booth in action</span></div>
```

and replace it with the corresponding block from the patch. `photos/site-frames.md`
lists which photo belongs to which label on which page.

## Verifying before it goes live

```bash
python3 -m http.server 8412 --directory /app/AU2
```

Then check: `index.html` (5 frames), `services.html` (3), `about.html` (4),
`portfolio.html` (6, including the before/after slider). Every `.ph` that got a
photo carries the class `has-photo`, so this counts them:

```bash
grep -c has-photo index.html services.html about.html portfolio.html
```

Expected: 5, 3, 4, 6.

## Rebuilding from source instead

If you would rather not use the tarball, the sources are in
`photos/originals/` in this repo and the build is one command:

```bash
python3 -m pip install Pillow pillow-heif
python3 scripts/optimize-photos.py
cp photos/web/*.jpg photos/web/*.webp /app/AU2/assets/img/photos/
```

## Still empty after this

26 frames, all listed with reasons in `photos/site-frames.md`. The headline: the
four named builds on the site — Northern Light, Yellowjacket, Snowbird,
Resurrection — have no photos anywhere in the 424-photo Facebook archive.
