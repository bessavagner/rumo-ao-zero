#!/usr/bin/env bash
# Backup off-site do banco de produção: snapshot CONSISTENTE da friday -> Dropbox.
# Mantém o benefício de backup do Dropbox SEM sincronizar o arquivo .sqlite3 vivo
# (o que causava risco de corrupção). Guarda cópias com timestamp e poda as antigas.
# Bom de rodar via cron no jarvis (ex.: diário).
#
# Uso: scripts/backup-db-to-dropbox.sh
# Vars: REMOTE (default friday), REMOTE_DB, BACKUP_DIR, KEEP (qtd a manter, default 14).
set -euo pipefail

REMOTE="${REMOTE:-friday}"
REMOTE_DB="${REMOTE_DB:-/home/bessa/Documents/projetos/rumo_ao_zero/apps/backend/db.sqlite3}"
BACKUP_DIR="${BACKUP_DIR:-/home/bessa/Dropbox/backups/rumo_ao_zero}"
KEEP="${KEEP:-14}"
SNAP="/tmp/rumo-db-backup.$$.sqlite3"
STAMP="$(date +%Y%m%d-%H%M%S)"

mkdir -p "$BACKUP_DIR"
echo "[backup] snapshot consistente na friday..."
ssh "$REMOTE" "if command -v sqlite3 >/dev/null 2>&1; then sqlite3 '$REMOTE_DB' \".backup '$SNAP'\"; else python3 -c 'import sqlite3,sys; s=sqlite3.connect(sys.argv[1]); d=sqlite3.connect(sys.argv[2]); s.backup(d); s.close(); d.close()' '$REMOTE_DB' '$SNAP'; fi"

DEST="$BACKUP_DIR/db-$STAMP.sqlite3"
rsync -a "$REMOTE:$SNAP" "$DEST"
ssh "$REMOTE" "rm -f '$SNAP'"
gzip -f "$DEST"
echo "[backup] gravado: $DEST.gz"

# Poda: mantém só os $KEEP mais recentes.
ls -1t "$BACKUP_DIR"/db-*.sqlite3.gz 2>/dev/null | tail -n +"$((KEEP+1))" | while read -r old; do
  rm -f "$old"; echo "[backup] podado: $old"
done
