# Backend Rumo ao Zero — imagem pronta para Google Cloud Run.
# SQLite persiste num volume montado em /data (DB_PATH). Quando migrarmos de banco,
# basta trocar DB_PATH/DATABASES e remover o volume — o resto continua igual.

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    DB_PATH=/data/db.sqlite3 \
    PATH="/app/.venv/bin:$PATH"

# uv (mesmo gestor de pacotes do projeto)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# 1) Dependências (camada cacheável a partir do lockfile)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# 2) Código da aplicação
COPY . .

# 3) Estáticos servidos pelo whitenoise (admin + swagger)
RUN python manage.py collectstatic --noinput

# Volume de persistência do SQLite (Cloud Run: montar GCS/Filestore aqui)
RUN mkdir -p /data
VOLUME ["/data"]

# Cloud Run injeta $PORT (default 8080). O entrypoint roda migrate e sobe o gunicorn.
EXPOSE 8080
ENTRYPOINT ["/app/deploy/docker-entrypoint.sh"]
