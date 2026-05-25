# Deploy — backend Rumo ao Zero

Dois alvos: **systemd** (sempre rodando na sua máquina, agora) e **Docker / Cloud Run**
(futuro). O SQLite é persistido num arquivo; quando migrarmos de banco isso fica obsoleto.

---

## 1. systemd (serviço de usuário, sempre rodando)

Roda como você (sem root), gunicorn em `127.0.0.1:8492` (porta incomum, só localhost).

```bash
# instalar a unit como serviço de usuário
mkdir -p ~/.config/systemd/user
ln -sf "$PWD/deploy/rumo-backend.service" ~/.config/systemd/user/rumo-backend.service
systemctl --user daemon-reload
systemctl --user enable --now rumo-backend.service

# sobreviver a logout/reboot sem você logar
loginctl enable-linger "$USER"

# conferir
systemctl --user status rumo-backend.service
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8492/api/schema/
```

- **Trocar a porta:** edite `Environment=PORT=` na unit e `systemctl --user daemon-reload && systemctl --user restart rumo-backend.service`.
- **Logs:** `journalctl --user -u rumo-backend.service -f`
- **Parar/desativar:** `systemctl --user disable --now rumo-backend.service`
- Como é symlink para o arquivo no repo, editar a unit + `daemon-reload` basta (sem recopiar).

> A unit roda `migrate` e `collectstatic` no `ExecStartPre`, então fica sempre consistente.

---

## 2. Docker (local)

```bash
docker build -t rumo-backend .
# volume nomeado para o SQLite persistir entre execuções
docker volume create rumo-data
docker run --rm -p 8492:8080 \
  -e SECRET_KEY="$(openssl rand -hex 32)" \
  -e DEBUG=False \
  -e ALLOWED_HOSTS=localhost,127.0.0.1 \
  -v rumo-data:/data \
  rumo-backend
# criar superuser dentro do container (uma vez):
docker run --rm -it -v rumo-data:/data rumo-backend python manage.py createsuperuser
```

O banco fica em `/data/db.sqlite3` (no volume `rumo-data`).

---

## 3. Google Cloud Run

Cloud Run tem filesystem efêmero — o SQLite **precisa** de um volume montado em `/data`.

### Variáveis de ambiente (no serviço Cloud Run)
| Var | Valor |
|---|---|
| `SECRET_KEY` | aleatória (use Secret Manager) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `SEU-SERVICO-xxxx.run.app` |
| `CSRF_TRUSTED_ORIGINS` | `https://SEU-SERVICO-xxxx.run.app` (para login no admin) |
| `DB_PATH` | `/data/db.sqlite3` |
| `WEB_CONCURRENCY` | `1` (ver caveat do SQLite) |

### Passos
```bash
# 1. build + push (Artifact Registry)
gcloud artifacts repositories create rumo --repository-format=docker --location=us-central1
gcloud builds submit --tag us-central1-docker.pkg.dev/SEU_PROJETO/rumo/backend

# 2. deploy com volume de persistência
#    Opção A — Filestore (NFS): locking confiável p/ SQLite (recomendado)
#    Opção B — bucket GCS via gcsfuse: mais barato, locking fraco (risco sob escrita concorrente)
gcloud run deploy rumo-backend \
  --image us-central1-docker.pkg.dev/SEU_PROJETO/rumo/backend \
  --region us-central1 \
  --max-instances 1 --min-instances 0 \
  --set-env-vars DEBUG=False,DB_PATH=/data/db.sqlite3,WEB_CONCURRENCY=1,ALLOWED_HOSTS=SEU-SERVICO.run.app \
  --add-volume name=data,type=cloud-storage,bucket=SEU_BUCKET \
  --add-volume-mount volume=data,mount-path=/data
```

### Caveat do SQLite no Cloud Run (importante)
- **`--max-instances 1` e `WEB_CONCURRENCY=1`.** SQLite é um único arquivo; múltiplas
  instâncias/workers escrevendo via volume de rede corrompem o banco.
- **GCS (gcsfuse)** tem locking fraco — ok para uso single-user de baixíssima escrita, mas
  **Filestore** é mais seguro se quiser dormir tranquilo.
- Isso tudo **desaparece quando migrarmos para Postgres/Cloud SQL**: troca-se `DATABASES`
  no settings, removem-se volume e essas restrições, e o app escala normalmente.
