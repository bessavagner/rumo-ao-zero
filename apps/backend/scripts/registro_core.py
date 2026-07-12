"""Núcleo compartilhado de registro — usado pelo CLI (registro.py) E pelo servidor MCP (mcp_server.py).

Fonte única da verdade pra: auth na API, resolução de nome -> ID (get-or-create de substituição;
gatilho e estado são taxonomia FIXA — o assistente manda o código, ver `taxonomia()`), parsing de
data/hora e construção+POST dos registros DIÁRIO/CRAVING/SLIP/PULSO. Stdlib-only (urllib), pra
rodar tanto no CLI (python do sistema) quanto no venv MCP.

As funções `registrar_*` RETORNAM um dict e LEVANTAM `RegistroError` em falha (campo faltando,
erro da API). Quem chama formata a saída: o CLI imprime JSON + exit; o MCP devolve {"ok": ...}.

Credenciais: ../.secrets/dev.env (relativo a apps/backend/), mesmo arquivo do resto do projeto.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent.parent / ".secrets" / "dev.env"
SUBSTITUICAO_CATEGORIAS = ["oral", "movimento", "social", "cognitivo", "ambiental"]


class RegistroError(Exception):
    """Erro de validação/comunicação. `detalhe` carrega o corpo de erro da API quando houver."""

    def __init__(self, mensagem: str, detalhe=None):
        super().__init__(mensagem)
        self.detalhe = detalhe


# --------------------------------------------------------------------------- infra HTTP

def load_env(path: Path = ENV_PATH) -> dict:
    if not path.exists():
        raise RegistroError(f"credenciais não encontradas em {path}")
    env: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    return env


class Api:
    """Cliente HTTP minimalista com token DRF."""

    def __init__(self, base: str, token: str):
        self.base = base.rstrip("/")
        self.token = token

    @classmethod
    def connect(cls) -> "Api":
        env = load_env()
        base = env.get("DEV_API_BASE", "http://127.0.0.1:8492")
        data = urllib.parse.urlencode(
            {
                "username": env.get("DEV_SUPERUSER_USERNAME", ""),
                "password": env.get("DEV_SUPERUSER_PASSWORD", ""),
            }
        ).encode()
        try:
            req = urllib.request.Request(f"{base.rstrip('/')}/api/auth/token/", data=data)
            with urllib.request.urlopen(req, timeout=15) as resp:
                token = json.loads(resp.read()).get("token")
        except urllib.error.URLError as exc:
            raise RegistroError(f"falha ao autenticar/conectar em {base}: {exc}") from exc
        if not token:
            raise RegistroError("auth não retornou token (cheque credenciais)")
        return cls(base, token)

    def request(self, method: str, path: str, body: dict | None = None):
        url = f"{self.base}{path}"
        payload = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=payload, method=method)
        req.add_header("Authorization", f"Token {self.token}")
        if payload is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")
            try:
                detail = json.loads(detail)
            except json.JSONDecodeError:
                pass
            raise RegistroError(f"API {exc.code} em {method} {path}", detalhe=detail) from exc
        except urllib.error.URLError as exc:
            raise RegistroError(f"sem conexão com {url}: {exc}") from exc

    def get(self, path: str):
        return self.request("GET", path)

    def post(self, path: str, body: dict) -> dict:
        return self.request("POST", path, body)

    def patch(self, path: str, body: dict) -> dict:
        return self.request("PATCH", path, body)

    def delete(self, path: str):
        return self.request("DELETE", path)


# ----------------------------------------------------------------- resolução de nomes

def _results(payload) -> list:
    if isinstance(payload, dict):
        return payload.get("results", [])
    return payload


def resolve_by_name(api: Api, endpoint: str, nome: str, create_payload: dict) -> tuple[int, bool]:
    """Get-or-create por ``nome`` (case-insensitive). Retorna (id, criado?)."""
    nome = nome.strip()
    query = urllib.parse.urlencode({"search": nome})
    for item in _results(api.get(f"{endpoint}?{query}")):
        if str(item.get("nome", "")).strip().lower() == nome.lower():
            return item["id"], False
    created = api.post(endpoint, create_payload)
    return created["id"], True


def resolve_substituicao(api: Api, nome: str, categoria: str | None) -> tuple[int, bool]:
    query = urllib.parse.urlencode({"search": nome.strip()})
    for item in _results(api.get(f"/api/baseline/substitutions/?{query}")):
        if str(item.get("nome", "")).strip().lower() == nome.strip().lower():
            return item["id"], False
    if not categoria:
        raise RegistroError(
            f"substituição '{nome}' é nova; informe a categoria ({'/'.join(SUBSTITUICAO_CATEGORIAS)})"
        )
    if categoria not in SUBSTITUICAO_CATEGORIAS:
        raise RegistroError(f"categoria inválida '{categoria}'", detalhe={"opcoes": SUBSTITUICAO_CATEGORIAS})
    created = api.post("/api/baseline/substitutions/", {"nome": nome.strip(), "categoria": categoria})
    return created["id"], True


# --------------------------------------------------------------------------- datas

def to_iso_date(value: str) -> str:
    """Aceita YYYY-MM-DD ou DD/MM (assume ano corrente). Retorna ISO."""
    value = value.strip()
    if "/" in value:
        parts = value.split("/")
        dd, mm = parts[0], parts[1]
        yyyy = parts[2] if len(parts) > 2 else str(date.today().year)
        if len(yyyy) == 2:
            yyyy = "20" + yyyy
        return f"{int(yyyy):04d}-{int(mm):02d}-{int(dd):02d}"
    return value


def to_iso_datetime(data: str, hora: str) -> str:
    hh, _, mm = hora.strip().partition(":")
    return f"{to_iso_date(data)}T{int(hh):02d}:{int(mm or 0):02d}"


# ------------------------------------------------------------------------ taxonomia

def taxonomia(api: Api) -> dict:
    """As situações e os estados válidos, achatados. É daqui que o assistente tira o código.

    A taxonomia é FIXA (mora em código no backend): não há get-or-create, não há criação. Mandar
    um código fora da lista dá 400 — o que é o ponto: a normalização acontece na entrada.
    """
    gatilhos = api.get("/api/taxonomia/gatilhos/")
    situacoes = [
        {"codigo": s["codigo"], "rotulo": s["rotulo"], "categoria": g["categoria"]}
        for g in gatilhos["grupos"]
        for s in g["situacoes"]
    ]
    situacoes += [
        {"codigo": s["codigo"], "rotulo": s["rotulo"], "categoria": None}
        for s in gatilhos["sem_categoria"]
    ]
    return {"situacoes": situacoes, "estados": api.get("/api/taxonomia/estados/")["estados"]}


# ------------------------------------------------------------------- operações de registro

def registrar_pulso(api: Api, *, data, hora, humor, energia, craving=None, estados=None, nota=None) -> dict:
    payload: dict = {"timestamp": to_iso_datetime(data, hora), "humor": humor, "energia": energia}
    if craving is not None:
        payload["craving"] = craving
    if nota:
        payload["nota"] = nota
    if estados:
        payload["estados"] = list(estados)
    created = api.post("/api/log/pulsos/", payload)
    return {"tipo": "PULSO", "id": created["id"], "timestamp": created["timestamp"], "criados": []}


def registrar_diario(
    api: Api, *, data, humor, energia, sono_h, sono_q,
    craving_pico=None, estados=None, linhas=None, corpo=None, boa=None, dificil=None,
) -> dict:
    payload: dict = {
        "data": to_iso_date(data), "humor": humor, "energia": energia,
        "sono_h": sono_h, "sono_q": sono_q,
    }
    if craving_pico is not None:
        payload["craving_pico"] = craving_pico
    for field, val in (("algo_do_corpo", corpo), ("coisa_boa", boa), ("coisa_dificil", dificil)):
        if val:
            payload[field] = val
    for i, linha in enumerate((linhas or [])[:3], start=1):
        payload[f"linha_{i}"] = linha
    if estados:
        payload["estados"] = list(estados)
        payload["estado_checado"] = True
    created = api.post("/api/log/daily/", payload)
    return {"tipo": "DIARIO", "id": created["id"], "data": created["data"], "criados": []}


def registrar_craving(
    api: Api, *, data, hora, substancia, intensidade_pico, gatilho,
    gatilhos_adicionais=None, detalhes=None, estados=None, fiz=None, fiz_categoria=None,
    duracao_min=None, intensidade_final=None, tempo_baixar_3=None, aprendizado=None,
) -> dict:
    """`gatilho` é um CÓDIGO da taxonomia (ver `taxonomia()`), não texto livre.

    A fala inteira do Bessa vai para `detalhes` — o texto nunca se perde, e o mapa não vira lixo.
    """
    if not gatilho:
        raise RegistroError("craving exige 'gatilho' (código da taxonomia; veja a tool taxonomia)")
    payload: dict = {
        "timestamp": to_iso_datetime(data, hora), "substancia": substancia,
        "intensidade_pico": intensidade_pico, "gatilho": gatilho,
    }
    if gatilhos_adicionais:
        payload["gatilhos_adicionais"] = list(gatilhos_adicionais)
    if detalhes:
        payload["detalhes"] = detalhes
    if estados:
        payload["estados"] = list(estados)
    for field, val in (
        ("duracao_min", duracao_min),
        ("intensidade_final", intensidade_final),
        ("tempo_para_baixar_3", tempo_baixar_3),
    ):
        if val is not None:
            payload[field] = val
    if aprendizado:
        payload["aprendizado"] = aprendizado
    criados: list[str] = []
    if fiz:
        sid, novo = resolve_substituicao(api, fiz, fiz_categoria)
        payload["substituicao_usada"] = sid
        if novo:
            criados.append(f"substituicao:{fiz}")
    created = api.post("/api/log/cravings/", payload)
    return {"tipo": "CRAVING", "id": created["id"], "timestamp": created["timestamp"], "criados": criados}


def registrar_slip(
    api: Api, *, data, hora, substancia, gatilho,
    gatilhos_adicionais=None, detalhes=None, quantidade=None, contexto=None, aprendizado=None,
    reset_alcool=False, reset_tabaco=False,
) -> dict:
    if not gatilho:
        raise RegistroError("slip exige 'gatilho' (código da taxonomia; veja a tool taxonomia)")
    payload: dict = {
        "timestamp": to_iso_datetime(data, hora), "substancia": substancia, "gatilho": gatilho,
    }
    if gatilhos_adicionais:
        payload["gatilhos_adicionais"] = list(gatilhos_adicionais)
    for field, val in (
        ("detalhes", detalhes), ("quantidade", quantidade),
        ("contexto", contexto), ("aprendizado", aprendizado),
    ):
        if val:
            payload[field] = val
    if reset_alcool:
        payload["reset_streak_alcool"] = True
    if reset_tabaco:
        payload["reset_streak_tabaco"] = True
    created = api.post("/api/log/slips/", payload)
    return {"tipo": "SLIP", "id": created["id"], "timestamp": created["timestamp"], "criados": []}
