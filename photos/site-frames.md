# appearance-unlimited.com image frames

Working copy of the site: `/app/appearance-unlimited-site` (a git snapshot of
the live site as deployed on 2026-09-08, plus one commit of changes). Photos
come from `photos/originals/` via `scripts/optimize-photos.py`; the built
variants are copied into `assets/img/photos/`.

## Filled — 18 frames

| Page | Frame label it replaced | Photo | Subject |
|---|---|---|---|
| index | Collision repair — panel work in the body bay | `collision-panel-work-body-bay` | Jeep Grand Cherokee quarter stripped and filled |
| index | Premium detailing — gloss finish close-up | `gloss-finish-close-up` | mirror-gloss red panel |
| index | Custom paint — spray booth in action | `custom-paint-spray-booth` | masked pickup in the booth |
| index | Classic restoration — bare-metal project on rotisserie | `bare-metal-classic-project` | Dodge D150 stripped at the front end |
| index | Shop floor — technicians at work, wide shot | `technicians-on-the-shop-floor` | two techs on a truck on the lift |
| services | Frame rack — unibody measurement in progress | `structural-repair-on-the-lift` | tech working under a raised vehicle |
| services | Paint booth — fresh basecoat, gloss black | `fresh-finish-in-the-booth` | masked front bumper assembly, fresh finish |
| services | Restoration bay — classic body shell on rotisserie | `classic-body-shell-in-primer` | 60s convertible in primer on the lift |
| about | Paint booth — downdraft spray environment | `downdraft-paint-booth` | masked vehicle inside the booth |
| about | Frame rack — structural straightening & measurement | `rocker-and-structural-repair` | rocker/structural repair on the lift |
| about | Detail bay — correction & finishing stations | `refinished-parts-finishing-stations` | refinished trim and lamps on the stands |
| about | Restoration bay — long-term project builds | `long-term-restoration-bay` | Chevy II mid-build |
| portfolio | BEFORE — barn-find condition | `dodge-d150-restoration--before` | D150 as delivered |
| portfolio | AFTER — showroom finish | `dodge-d150-restoration--after` | same D150, fresh light blue |
| portfolio | Collision — before | `collision-damage-before` | crushed rear bumper |
| portfolio | Collision — after | `collision-repair-after` | repaired black pickup |
| portfolio | Paint correction — results | `paint-correction-results` | deep gloss down a black pickup |
| portfolio | Premium full detail — results | `premium-full-detail-results` | finished olive green Ram 1500 |

The before/after slider pair is the only true same-vehicle, same-angle pair in
the archive, so it is the one that carries the `--before` / `--after` suffix.

## Left empty, and what each one needs

Nothing in the 424-photo archive honestly matches these. Filling them would
have meant captioning one vehicle as another on a live commercial site.

**Named builds — 21 frames across 5 pages.** `index` (2), `portfolio` (3),
`build-northern-light` (7), `build-yellowjacket` (6), `build-resurrection` (5)
all name a specific car: a 1969 Camaro SS, a 1966 Chevy C10, a 1966 Mustang
coupe, a 1957 Bel Air. **None of those four cars appears anywhere in the
archive.** These need the shop's own photos of those builds — or the pages need
to be rebuilt around builds that were actually photographed.

The obvious candidate is already in hand: the **Dodge D150 "GRYFIN"**
restoration is documented end to end — arrival, teardown, bed and floor work,
bodywork, primer, paint, finished — which is exactly the six-stage shape
`build-*.html` expects. Two others have partial coverage: a 1965 Buick Riviera
Gran Sport (finished, in light blue) and a Toyota FJ40 (finished, light blue).

**about — "Shop exterior — Holiday Hills Dr".** The archive has vehicles parked
outside the building but no clean shot of the shop itself. One phone photo of
the frontage fixes this.

**services — "Detail bay — paint correction under inspection lights".** The
archive is body-shop work almost exclusively; there is no detailing or paint
correction photo in it. Worth noting the site calls the shop "Northern
Michigan's largest detailing operation" — that claim currently has no picture
behind it anywhere.

**contact — "Map — 3600 Holiday Hills Dr".** Wants a map embed, not a photo.

## Other things the pull turned up

* `assets/img/labor-day-ad.png` is referenced by `specials.html` and **404s on
  the live site**. It fails quietly (`onerror` hides it), so the promo section
  is running without its flyer.
* `assets/img/Chevyc10.png` — the yellow C10 used as YELLOWJACKET on four pages
  — is a stock photo of someone else's truck, not a shop build.
* The address disagrees: the site's schema says 3600 Holiday Hills Dr, the
  Facebook page says 2115 N US-31.
* The logo `<img>` on every page falls back to `../../home/jimbro/Downloads/au2.png`,
  a path from whoever's laptop built the draft. Harmless (it 404s and the text
  fallback takes over) but it should not be in a deployed page.
