#!/usr/bin/env bash
# Download the photos from the Appearance Unlimited Facebook page into photos/originals/.
#
# Facebook serves page photos only to logged-in sessions, so this script needs
# your browser cookies. Run it on a machine where you are logged into Facebook
# as someone with access to the page.
#
#   ./scripts/fetch-fb-photos.sh                      # uses Chrome cookies
#   ./scripts/fetch-fb-photos.sh --browser firefox
#   ./scripts/fetch-fb-photos.sh --cookies ./cookies.txt
#   ./scripts/fetch-fb-photos.sh --page someotherpage
#
# NOTE: for the website you want the ORIGINALS, not these. Facebook re-encodes
# uploads and caps them near 2048px on the long edge. Prefer, in order:
#   1. the shop's original camera files / phone camera roll
#   2. Meta Business Suite -> Settings -> Download page data (full-res export)
#   3. this script (scrape of the public/CDN copies) as the fallback
set -euo pipefail

PAGE="appearanceunlimited"
BROWSER="chrome"
COOKIE_FILE=""
DEST="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/photos/originals"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --page)    PAGE="$2"; shift 2 ;;
    --browser) BROWSER="$2"; shift 2 ;;
    --cookies) COOKIE_FILE="$2"; shift 2 ;;
    --dest)    DEST="$2"; shift 2 ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

if ! command -v gallery-dl >/dev/null 2>&1; then
  echo "==> installing gallery-dl"
  python3 -m pip install --quiet --upgrade gallery-dl
fi

if [[ -n "$COOKIE_FILE" ]]; then
  AUTH=(--cookies "$COOKIE_FILE")
else
  AUTH=(--cookies-from-browser "$BROWSER")
fi

mkdir -p "$DEST"
echo "==> downloading facebook.com/$PAGE photos -> $DEST"

# Page photo albums. Both URL forms are tried: FB moves pages between layouts.
for url in \
  "https://www.facebook.com/$PAGE/photos" \
  "https://www.facebook.com/$PAGE/photos_by"
do
  echo "--> $url"
  gallery-dl "${AUTH[@]}" \
    --dest "$DEST" \
    --directory "" \
    --filename "{id}.{extension}" \
    --write-metadata \
    --sleep 1.5-3.0 \
    --retries 4 \
    "$url" || echo "    (no results from $url)"
done

COUNT=$(find "$DEST" -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.webp' \) | wc -l | tr -d ' ')
echo "==> $COUNT image(s) in $DEST"
[[ "$COUNT" == "0" ]] && cat <<'MSG'

Nothing downloaded. Usual causes:
  * not logged into Facebook in the browser you pointed at (--browser)
  * the page slug is wrong (check the URL bar on the page itself)
  * Facebook served a checkpoint/login wall -- open the page in that browser
    first, then re-run
  * Chrome on macOS locks its cookie DB: quit Chrome, or export cookies to a
    Netscape-format file and use --cookies
MSG
exit 0
