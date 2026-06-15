#!/usr/bin/env bash
# Sync mão-única jarvis -> friday do CÓDIGO/DOCS do projeto "Rumo ao Zero".
#
# Por que mão-única (e não Dropbox): o jarvis é a fonte da verdade do código; a friday
# roda o backend (gunicorn) + o MCP a partir desta cópia. O BANCO (db.sqlite3) é
# propriedade da friday (capturas WhatsApp->MCP escrevem nele) e por isso é EXCLUÍDO
# daqui — para trazer dados frescos pro jarvis use scripts/pull-db-from-friday.sh.
#
# Reload na friday (gunicorn NÃO tem auto-reload):
#   - migrations/*.py  -> roda manage.py migrate no friday
#   - qualquer .py     -> restart do rumo-backend.service
#   - pyproject/uv.lock-> AVISA (sync de deps é manual no venv ~/.venvs/rumo-backend)
#
# Uso:
#   scripts/sync-to-friday.sh            # uma passada (rsync incremental)
#   scripts/sync-to-friday.sh --watch    # observa e sincroniza a cada alteração
#   scripts/sync-to-friday.sh --dry-run  # mostra o que mudaria, sem aplicar
#
# Variáveis: REMOTE (host ssh, default "friday"), DEST (caminho no remoto).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REMOTE="${REMOTE:-friday}"
DEST="${DEST:-/home/bessa/Documents/projetos/rumo_ao_zero/}"
REMOTE_ROOT="${DEST%/}"
EXCLUDE="$ROOT/scripts/sync-to-friday.exclude"
BACKEND_VENV="/home/bessa/.venvs/rumo-backend/bin/python"

remote_run() { ssh "$REMOTE" "cd '$REMOTE_ROOT' && $1"; }

post_sync() {
  local changes="$1"
  if printf '%s\n' "$changes" | grep -qE '/migrations/[^/]+\.py$'; then
    echo "[remote] migration detectada -> manage.py migrate"
    remote_run "cd apps/backend && $BACKEND_VENV manage.py migrate --noinput" 2>&1 | sed 's/^/[migrate] /'
  fi
  if printf '%s\n' "$changes" | grep -qE '[ /](pyproject\.toml|uv\.lock)$'; then
    echo "[remote] AVISO: deps Python mudaram — rode o sync de deps no venv da friday:"
    echo "         ssh $REMOTE 'cd $REMOTE_ROOT/apps/backend && uv pip sync ...'  (manual)"
  fi
  # gunicorn não recarrega sozinho: qualquer .py exige restart do backend.
  if printf '%s\n' "$changes" | grep -qE '\.py$'; then
    echo "[remote] código .py mudou -> restart rumo-backend.service"
    ssh "$REMOTE" 'systemctl --user restart rumo-backend.service' 2>&1 | sed 's/^/[restart] /' || \
      echo "[restart] FALHOU (rode na mão: ssh $REMOTE systemctl --user restart rumo-backend.service)"
  fi
}

do_sync() {
  local flags="$1" out
  out=$(rsync -azi $flags --delete --exclude-from="$EXCLUDE" "$ROOT/" "$REMOTE:$DEST" 2>/dev/null) || {
    echo "[sync] rsync falhou"; return 1; }
  if [ -n "$out" ]; then
    echo "[sync] $(date +%H:%M:%S) — $(printf '%s\n' "$out" | grep -c .) item(ns)"
    printf '%s\n' "$out" | sed 's/^/  /'
    [ "$flags" = "--dry-run" ] || post_sync "$out"
  fi
}

case "${1:-}" in
  --dry-run) echo "[sync] DRY-RUN -> $REMOTE:$DEST"; do_sync "--dry-run"; exit 0 ;;
  --watch)   : ;;  # cai no bloco de watch abaixo
  "")        do_sync ""; exit 0 ;;
  *)         echo "uso: $0 [--watch|--dry-run]"; exit 2 ;;
esac

echo "[sync] passada inicial -> $REMOTE:$DEST"
do_sync "" || true
if command -v inotifywait >/dev/null 2>&1; then
  echo "[sync] observando (inotify) $ROOT — Ctrl-C encerra"
  inotifywait -m -r -e modify,create,delete,move \
    --exclude '(/\.git/|/\.venv/|/\.codegraph/|/node_modules/|/__pycache__/|/\.ruff_cache/|/\.pytest_cache/|/staticfiles/|\.pyc$|/\.omc/|/\.claude/|db\.sqlite3)' \
    "$ROOT" 2>/dev/null | while read -r _; do
      sleep 0.3   # coalesce rajadas
      do_sync "" || true
    done
else
  echo "[sync] inotifywait ausente — polling a cada 2s (instale inotify-tools p/ event-driven)"
  while true; do sleep 2; do_sync "" || true; done
fi
