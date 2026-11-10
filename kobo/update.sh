#!/bin/sh
# Runs ON THE KOBO (BusyBox sh). Downloads today's calendar PNG into the sleep-screen folder.
# install-kobo-addon.ps1 copies this to /mnt/onboard/.adds/calendar/update.sh and fills in the URL.
URL="@@CALENDAR_URL@@"
BASE="/mnt/onboard/.adds/calendar"
DEST="/mnt/onboard/.kobo/screensaver/calendar.png"
TMP="$BASE/download.tmp"
LOG="$BASE/update.log"

mkdir -p "$BASE" "$(dirname "$DEST")"
log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "$LOG"; }

# keep the log small
if [ -f "$LOG" ] && [ "$(wc -c < "$LOG")" -gt 20000 ]; then
  tail -n 20 "$LOG" > "$LOG.new" && mv "$LOG.new" "$LOG"
fi

if command -v curl >/dev/null 2>&1; then
  TOOL=curl
  fetch() { curl -fsSL --max-time 40 -o "$TMP" "$URL"; }
else
  TOOL=wget
  fetch() { wget -q -T 40 -O "$TMP" "$URL"; }
fi

log "start ($TOOL)"
i=0
while [ "$i" -lt 12 ]; do        # Wi-Fi may still be connecting: retry for about a minute
  rm -f "$TMP"
  if fetch && [ -s "$TMP" ]; then break; fi
  i=$((i + 1))
  sleep 5
done

SIZE=$(wc -c < "$TMP" 2>/dev/null || echo 0)
if [ "$SIZE" -gt 50000 ]; then   # real calendar PNGs are ~200 KB; anything tiny is an error page
  if mv "$TMP" "$DEST"; then
    log "ok: $SIZE bytes"
    exit 0
  fi
fi
rm -f "$TMP"
log "FAILED after $i retries (size $SIZE)"
exit 1
