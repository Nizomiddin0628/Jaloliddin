#!/bin/bash
# Har kuni kechasi ishlaydigan zaxira nusxa.
# crontab -e ga qo'shiladi:  0 3 * * * /home/toy/app/backend/zaxira.sh

set -e
APP=/home/toy/app/backend
DEST=/home/toy/backups
STAMP=$(date +%F)

mkdir -p "$DEST/esdaliklar"

# Baza va ochiq media — kichik, har kuni to'liq nusxa
cd "$APP"
tar czf "$DEST/baza-$STAMP.tar.gz" db.sqlite3 media 2>/dev/null || true

# Esdaliklar — katta, shuning uchun faqat yangilarini nusxalaymiz
if command -v rsync >/dev/null 2>&1; then
    rsync -a "$APP/private_media/" "$DEST/esdaliklar/"
else
    cp -au "$APP/private_media/." "$DEST/esdaliklar/" 2>/dev/null || true
fi

# Bir haftadan eski arxivlarni tozalaymiz, disk to'lmasin
find "$DEST" -maxdepth 1 -name "baza-*.tar.gz" -mtime +7 -delete

echo "$(date '+%F %T') zaxira tayyor" >> "$DEST/zaxira.log"