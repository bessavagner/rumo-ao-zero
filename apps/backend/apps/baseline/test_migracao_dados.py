"""A migração executa uma decisão humana versionada. Pós Task 7, os models legados
(`CravingEvent.gatilho_texto`, `EstadoInterno`) já saíram do código e a migração de dados real
já rodou e foi verificada — o que sobra para testar aqui é a LÓGICA PURA que ainda vive (e que
vai rodar de novo na friday): os helpers de `_0008_helpers` e `taxonomia.carregar_mapa`. Nenhum
model é instanciado — por isso não precisa de `@pytest.mark.django_db`.
"""

import csv

from apps.baseline import taxonomia
from apps.log.migrations import _0008_helpers as helpers


def test_situacao_texto_que_casa_vira_codigo_do_mapa():
    mapa = {"fim de expediente": "fim_expediente"}
    assert helpers._situacao(mapa, "fim de expediente") == "fim_expediente"


def test_situacao_texto_que_nao_casa_vira_outro():
    assert helpers._situacao({}, "uma coisa que só eu entendo") == "outro"


def test_situacao_texto_vazio_vira_outro():
    mapa = {"fim de expediente": "fim_expediente"}
    assert helpers._situacao(mapa, "") == "outro"
    assert helpers._situacao(mapa, None) == "outro"


def test_situacao_casa_sobre_texto_normalizado():
    # "Fim de Expediente" (maiúsculas) precisa casar com a chave normalizada do mapa.
    mapa = {"fim de expediente": "fim_expediente"}
    assert helpers._situacao(mapa, "Fim de Expediente") == "fim_expediente"


def test_carregar_mapa_arquivo_inexistente_devolve_vazio(tmp_path, monkeypatch):
    monkeypatch.setattr(taxonomia, "MAPAS_DIR", tmp_path)
    assert taxonomia.carregar_mapa("nao_existe") == {}


def test_carregar_mapa_ignora_linha_com_codigo_vazio(tmp_path, monkeypatch):
    monkeypatch.setattr(taxonomia, "MAPAS_DIR", tmp_path)
    caminho = tmp_path / "gatilhos.csv"
    with caminho.open("w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=["texto_original", "ocorrencias", "codigo", "regra"])
        escritor.writeheader()
        escritor.writerow({
            "texto_original": "algo indecifrável", "ocorrencias": 1,
            "codigo": "", "regra": "SEM CORRESPONDENCIA",
        })
        escritor.writerow({
            "texto_original": "fim de expediente", "ocorrencias": 2,
            "codigo": "fim_expediente", "regra": "casou: fim de expediente",
        })

    mapa = taxonomia.carregar_mapa("gatilhos")

    # A célula `codigo` vazia não entra no mapa: na migração, esse texto cai em "outro" e o
    # original é preservado em `detalhes` (é o helper `_situacao` acima que garante isso).
    assert mapa == {"fim de expediente": "fim_expediente"}
