# Backend — Rumo ao Zero

API Django REST para registro de cessação (tabaco + álcool) e backlog do projeto.
Spec: `../../docs/.ai/reports/003_api_backend/000_proposta_api.md`.

- **Stack:** Django 5 + DRF, SQLite, gestão de pacotes com `uv`.
- **Single-user** agora, estrutura pronta para multi-user.
- Banco em `db.sqlite3` (a pasta vive no Dropbox → backup coberto).

## Rodar

```bash
cd apps/backend
uv run python manage.py migrate
uv run python manage.py createsuperuser   # 1ª vez
uv run python manage.py runserver
```

- Admin: http://127.0.0.1:8000/admin/
- API (browsable): http://127.0.0.1:8000/api/
- Docs (Swagger): http://127.0.0.1:8000/api/docs/

## Testes

```bash
uv run pytest
```

## Autenticação para ingestão programática

```bash
# obter token (usuário já criado)
curl -s -X POST http://127.0.0.1:8000/api/auth/token/ \
  -d "username=SEU_USER&password=SUA_SENHA"
# -> {"token": "..."}

# usar o token nos POSTs
curl -s -X POST http://127.0.0.1:8000/api/log/daily/ \
  -H "Authorization: Token SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"data":"2026-05-25","humor":3,"energia":4,"sono_h":"7.0","sono_q":4,"craving_pico":2,"estados":[]}'
```

O campo `user` nunca vai no payload — é inferido do token.

## Endpoints principais

| Recurso | Rota |
|---|---|
| Diário | `/api/log/daily/` |
| Cravings | `/api/log/cravings/` |
| Slips | `/api/log/slips/` |
| Baseline (Dia 0) | `/api/baseline/profile/` |
| Substituições / Valores / If-Then | `/api/baseline/{substitutions,values,ifthen}/` |
| Taxonomia de gatilhos / estados (read-only) | `/api/taxonomia/gatilhos/`, `/api/taxonomia/estados/` |
| Backlog (itens) | `/api/backlog/items/` |
| Decisões (ADR) | `/api/backlog/decisions/` |
| Consultas | `/api/backlog/consultas/` |
| Compras | `/api/backlog/compras/` |

Filtros via query string, ex.: `/api/backlog/items/?secao=saude&status=pendente`.

## Fluxo de uso atual

1. Capturo no celular (Google Keep / Notas Motorola).
2. Colo a transcrição na conversa com o assistente.
3. O assistente faz `POST` autenticado nos endpoints (servidor local no ar).
4. Backlog é preenchido pelo assistente em `/api/backlog/*` conforme instruções.
