#!/usr/bin/env bash
# Traz uma cópia CONSISTENTE do banco de produção (friday) para o jarvis.
# O banco é PROPRIEDADE da friday (capturas WhatsApp->MCP escrevem nele); este é o
# único caminho friday->jarvis. Usa sqlite .backup (snapshot atômico, seguro com o
# gunicorn escrevendo) — NUNCA copie o arquivo .sqlite3 vivo direto.
#
# Uso: scripts/pull-db-from-friday.sh
# Vars: REMOTE (default friday), REMOTE_DB, LOCAL_DB.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REMOTE="${REMOTE:-friday}"
REMOTE_DB="${REMOTE_DB:-/home/bessa/Documents/projetos/rumo_ao_zero/apps/backend/db.sqlite3}"
LOCAL_DB="${LOCAL_DB:-$ROOT/apps/backend/db.sqlite3}"
SNAP="/tmp/rumo-db-snapshot.$$.sqlite3"

echo "[pull] snapshot consistente na friday..."
ssh "$REMOTE" "if command -v sqlite3 >/dev/null 2>&1; then sqlite3 '$REMOTE_DB' \".backup '$SNAP'\"; else python3 -c 'import sqlite3,sys; s=sqlite3.connect(sys.argv[1]); d=sqlite3.connect(sys.argv[2]); s.backup(d); s.close(); d.close()' '$REMOTE_DB' '$SNAP'; fi"

if [ -f "$LOCAL_DB" ]; then
  BK="$LOCAL_DB.bak.$(date +%Y%m%d-%H%M%S)"
  cp -a "$LOCAL_DB" "$BK"
  echo "[pull] backup do db local anterior -> $BK"
fi

echo "[pull] copiando snapshot friday -> jarvis..."
rsync -a "$REMOTE:$SNAP" "$LOCAL_DB"
ssh "$REMOTE" "rm -f '$SNAP'"
echo "[pull] pronto: $LOCAL_DB"
