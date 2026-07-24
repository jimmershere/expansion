# marketplace-scout-android

The phone version of [`marketplace-scout`](../marketplace-scout/): a native
Android app (Kotlin, min SDK 26 / Android 8+) that runs the same pipeline
entirely on the phone —

sweep NC-area Facebook Marketplace for **classic pickups, classic cars,
90s import tuners, and custom vehicles** → normalize year/make/model/mileage →
score **clean-Carfax likelihood** from listing text → research an **average
northern-US resale value** per vehicle from comparable listings in 11 northern
metros (trimmed median) → export the deals ≥15% below market as an **`.xlsx`**
with `Make · Model · Year · Mileage · Clean Carfax · URL · Avg Resale Price
(Northern US)` plus asking price, $/% below market, location, category, notes.

Where the desktop tool drives Playwright, the app drives the **WebView on
screen** — you log into Facebook in it once, and the sweep browses exactly as
you would, with random 2–6 s delays and page caps.

## Build & install

1. Open `marketplace-scout-android/` in **Android Studio** (Hedgehog or newer);
   let it sync Gradle.
2. `Run ▶` on your phone (USB debugging), or **Build → Build APK** and
   sideload `app/build/outputs/apk/debug/app-debug.apk`.

No Play Store, no server, no account other than your own Facebook login.

## Use

1. **Login** — opens facebook.com in the app; log in once (cookies persist).
2. **Run sweep** — walks every category × area × query, then detail pages,
   then northern-metro comps. Status line shows live progress. The screen
   stays on: **keep the app in the foreground** — Android pauses WebViews in
   the background, so a backgrounded sweep simply stalls until you return.
3. **Share results** — Android share sheet with the `.xlsx`. Pick **Google
   Drive/Sheets** to land it as a Google spreadsheet, or Gmail/Messages/etc.

A full sweep is a lot of page loads at polite speeds — expect it to take a
while. Comp medians are cached for 14 days, so the second run is much faster.

## Where things live

| File | Role |
|---|---|
| `core/Config.kt` | Areas, northern comp metros, category queries, filters, pacing — edit and rebuild |
| `web/Scripts.kt` | All Facebook-specific JavaScript (card/detail extraction). **If a sweep returns 0 cards, patch here** |
| `web/MarketplaceDriver.kt` | WebView driving: load/scroll/extract, login detection, rate limits |
| `core/Normalize.kt` `core/Carfax.kt` `core/CompsEngine.kt` | Same logic as the desktop tool, ported to Kotlin |
| `export/MiniXlsx.kt` | Zero-dependency `.xlsx` writer |
| `ScoutController.kt` | The sweep pipeline (`mscout run` equivalent) |

## Honest limitations (same as the desktop tool, plus phone realities)

- **Facebook ToS / blocking.** No public API exists; this automates your own
  logged-in session. Polite pacing is built in, but keep runs modest — heavy
  use risks an account checkpoint. Use at your own risk.
- **Foreground only.** WebViews don't run reliably in background/Doze, so the
  sweep needs the app on screen (it keeps the screen awake itself). Plug the
  phone in for a full sweep.
- **Clean Carfax is inferred, not verified** — 1/0/blank from seller claims
  and red-flag keywords; VINs found in ads go into Notes so you can pull a
  real report before buying.
- **"Avg resale" is a trimmed median of live asking prices** in northern
  metros — a solid proxy that runs a few percent above true sold prices.
- **Selectors rot.** Facebook changes markup constantly; everything
  FB-specific is isolated in `web/Scripts.kt` for quick patching.
