"""O core do MCP/CLI só monta payload e chama a API. Testamos o payload, não a rede."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import registro_core as core  # noqa: E402


class ApiFake:
    def __init__(self):
        self.posts = []
        self.respostas = {
            "/api/taxonomia/gatilhos/": {
                "grupos": [
                    {
                        "categoria": "conflito_outros",
                        "rotulo": "Conflito com outros",
                        "situacoes": [{"codigo": "discussao_atrito", "rotulo": "Discussão / atrito"}],
                    }
                ],
                "sem_categoria": [{"codigo": "outro", "rotulo": "Outro"}],
            },
            "/api/taxonomia/estados/": {"estados": [{"codigo": "raiva", "rotulo": "Raiva"}]},
            "/api/taxonomia/substituicoes/": {
                "substituicoes": [
                    {"codigo": "movimento",
                     "rotulo": "Movimento — andar, correr, alongar, qualquer coisa com o corpo"},
                ]
            },
        }

    def get(self, path):
        return self.respostas[path]

    def post(self, path, body):
        self.posts.append((path, body))
        return {"id": 1, "timestamp": body.get("timestamp"), "data": body.get("data")}


def test_taxonomia_achata_situacoes_com_categoria():
    api = ApiFake()
    t = core.taxonomia(api)
    assert {"codigo": "discussao_atrito", "rotulo": "Discussão / atrito",
            "categoria": "conflito_outros"} in t["situacoes"]
    assert {"codigo": "outro", "rotulo": "Outro", "categoria": None} in t["situacoes"]
    assert t["estados"] == [{"codigo": "raiva", "rotulo": "Raiva"}]


def test_registrar_craving_manda_codigo_e_joga_a_fala_em_detalhes():
    api = ApiFake()
    core.registrar_craving(
        api, data="2026-07-12", hora="18:30", substancia="tabaco", intensidade_pico=8,
        gatilho="discussao_atrito", detalhes="bati de frente com o chefe",
        estados=["raiva"], gatilhos_adicionais=["fim_expediente"],
    )
    caminho, corpo = api.posts[0]
    assert caminho == "/api/log/cravings/"
    assert corpo["gatilho"] == "discussao_atrito"
    assert corpo["gatilhos_adicionais"] == ["fim_expediente"]
    assert corpo["detalhes"] == "bati de frente com o chefe"
    assert corpo["estados"] == ["raiva"]
    assert "gatilho_texto" not in corpo and "trigger" not in corpo


def test_registrar_craving_exige_o_gatilho():
    api = ApiFake()
    with pytest.raises(core.RegistroError):
        core.registrar_craving(
            api, data="2026-07-12", hora="18:30", substancia="tabaco",
            intensidade_pico=8, gatilho="",
        )


def test_nao_existe_mais_caminho_de_criacao_de_gatilho():
    for sumiu in ("resolve_trigger", "buscar_trigger", "editar_gatilho", "resolve_estado"):
        assert not hasattr(core, sumiu), f"{sumiu} ainda existe — a porta continua aberta"


def test_taxonomia_traz_as_substituicoes():
    api = ApiFake()
    t = core.taxonomia(api)
    assert {"codigo": "movimento",
            "rotulo": "Movimento — andar, correr, alongar, qualquer coisa com o corpo"} in t["substituicoes"]


def test_registrar_craving_manda_categoria_e_a_fala_em_detalhes():
    api = ApiFake()
    core.registrar_craving(
        api, data="2026-07-13", hora="18:30", substancia="tabaco", intensidade_pico=8,
        gatilho="tedio_vazio", substituicao="movimento", substituicao_detalhes="fui correr",
    )
    _, corpo = api.posts[0]
    assert corpo["substituicao"] == "movimento"
    assert corpo["substituicao_detalhes"] == "fui correr"
    assert "substituicao_usada" not in corpo and "fiz" not in corpo


def test_nao_existe_mais_get_or_create_de_substituicao():
    for sumiu in ("resolve_substituicao", "resolve_by_name", "SUBSTITUICAO_CATEGORIAS"):
        assert not hasattr(core, sumiu), f"{sumiu} ainda existe — a porta continua aberta"
