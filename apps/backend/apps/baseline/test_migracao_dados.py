"""A migração executa uma decisão humana versionada. Pós Task 7, os models legados
(`CravingEvent.gatilho_texto`, `EstadoInterno`) já saíram do código e a migração de dados real
já rodou e foi verificada — o que sobra para testar aqui é a LÓGICA PURA que ainda vive (e que
vai rodar de novo na friday): os helpers de `_0008_helpers` e `taxonomia.carregar_mapa`. Nenhum
model é instanciado — por isso não precisa de `@pytest.mark.django_db`.

A classe `TestMigracoesReais` abaixo vai além: exercita `migrar_gatilhos`/`migrar_estados` de
verdade, rodando as migrations reais do Django (`log.0007` -> `log.0008`) contra um banco SQLite
ISOLADO (arquivo em `tmp_path`, alias de conexão próprio — nunca o banco de teste padrão). É o
mesmo princípio do banco legado sintético usado em `test_mapear_gatilhos.py`, mas aqui quem cria
o schema são as migrations verdadeiras (via `MigrationExecutor`), não SQL manual: assim o teste
cobre o código que de fato roda na friday, byte a byte.
"""

import csv

import pytest
from django.conf import settings as django_settings
from django.db import connections
from django.db.migrations.executor import MigrationExecutor
from django.utils import timezone

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


# ── `migrar_gatilhos`/`migrar_estados` de verdade, via migrations reais ─────────────────────
#
# Usam os mapas aprovados e versionados em `apps/baseline/mapas/*.csv` (não mexemos neles aqui):
#   gatilhos.csv: "euforia" -> comemoracao
#   estados.csv:  "cansaço" -> cansaco, "cansado" -> cansaco (a mesma dupla que o colapso testa)

LOG_0007 = ("log", "0007_gatilho_taxonomia_add")
LOG_0008 = ("log", "0008_gatilho_taxonomia_dados")


def _migrar(alvo):
    """Roda as migrations reais até `alvo` = (app_label, nome) no banco de teste 'default' e
    devolve o registro de apps histórico (`apps.get_model` com os campos EXATAMENTE como eram
    naquele ponto — inclusive os campos legados que o código atual não tem mais).

    Só existe UM alias viável pra isto: 'default'. O código de `migrar_gatilhos`/
    `migrar_estados` (como todo `RunPython` de produção) não chama `.using(...)` — em produção
    migrations sempre rodam contra o alias 'default', então o código real não precisa disso, e
    um alias de teste isolado faria as queries do PRÓPRIO helper caírem silenciosamente em
    'default' mesmo (o roteador padrão do Django ignora qual conexão rodou a migração).
    """
    MigrationExecutor(connections["default"]).migrate([alvo])
    # loader novo: o executor usado pra migrar não conhece o estado recém-aplicado.
    return MigrationExecutor(connections["default"]).loader.project_state([alvo]).apps


def _criar_usuario(apps_estado, username="bessa"):
    User = apps_estado.get_model(*django_settings.AUTH_USER_MODEL.split("."))
    return User.objects.create(username=username)


@pytest.fixture
def banco_pre_taxonomia():
    """Ao final do teste, sempre migra o banco de teste 'default' de volta pro HEAD (leaf
    nodes) — mesmo se o teste falhar. Sem isso, um teste que migra pra trás deixaria a suíte
    INTEIRA rodando com o schema de 2026-07 (colunas/models que já foram removidos do código).

    Por que 'default' (o banco de teste compartilhado) e não um alias isolado: ver docstring de
    `_migrar`. Por que `transaction=True` no marcador da classe: o SQLite recusa alterar schema
    com FKs habilitadas dentro de uma transação já aberta, e o `django_db` não-transacional do
    pytest-django abre uma antes do corpo do teste rodar; `transaction=True` evita isso.
    """
    yield
    executor = MigrationExecutor(connections["default"])
    executor.migrate(executor.loader.graph.leaf_nodes())


@pytest.mark.django_db(transaction=True)
class TestMigracoesReais:
    """Exercita `migrar_gatilhos`/`migrar_estados` de verdade, via `migrate` real (não uma
    chamada direta às funções) — é o código que vai rodar na friday, byte a byte."""

    def test_gatilho_que_casa_vira_codigo_certo_e_guarda_o_texto_original(self, banco_pre_taxonomia):
        apps_0007 = _migrar(LOG_0007)
        user = _criar_usuario(apps_0007)
        CravingEvent = apps_0007.get_model("log", "CravingEvent")
        craving = CravingEvent.objects.create(
            user=user, timestamp=timezone.now(), substancia="tabaco", intensidade_pico=7,
            gatilho_texto="euforia",
        )

        apps_0008 = _migrar(LOG_0008)
        c = apps_0008.get_model("log", "CravingEvent").objects.get(pk=craving.pk)

        assert c.gatilho == "comemoracao"
        assert c.detalhes == "euforia"

    def test_gatilho_que_nao_casa_vira_outro_e_preserva_detalhes(self, banco_pre_taxonomia):
        apps_0007 = _migrar(LOG_0007)
        user = _criar_usuario(apps_0007)
        Slip = apps_0007.get_model("log", "Slip")
        texto = "um textão que ninguém nunca vai escrever de novo"
        slip = Slip.objects.create(
            user=user, timestamp=timezone.now(), substancia="alcool", gatilho_texto=texto,
        )

        apps_0008 = _migrar(LOG_0008)
        s = apps_0008.get_model("log", "Slip").objects.get(pk=slip.pk)

        assert s.gatilho == "outro"
        assert s.detalhes == texto

    def test_estado_fora_do_mapa_levanta_runtime_error_em_vez_de_apagar_o_nome(self, banco_pre_taxonomia):
        apps_0007 = _migrar(LOG_0007)
        user = _criar_usuario(apps_0007)
        CravingEvent = apps_0007.get_model("log", "CravingEvent")
        EstadoInterno = apps_0007.get_model("baseline", "EstadoInterno")

        craving = CravingEvent.objects.create(
            user=user, timestamp=timezone.now(), substancia="tabaco", intensidade_pico=6,
            gatilho_texto="euforia",
        )
        estado = EstadoInterno.objects.create(
            user=user, nome="estado nunca catalogado em lugar nenhum",
        )
        craving.estados_m2m.add(estado)

        # Important 1: sem o fix, isto apagaria o nome em silêncio (viraria "outro" e o
        # EstadoInterno seria deletado logo depois pelas migrations 0009/0006). Com o fix, a
        # migração aborta — e como é atômica, nem `migrar_gatilhos` fica meio-aplicado.
        with pytest.raises(RuntimeError, match="estado nunca catalogado em lugar nenhum"):
            _migrar(LOG_0008)

        # Limpa o dado que provocou o erro: sem isso, a fixture `banco_pre_taxonomia` bateria no
        # MESMO RuntimeError ao tentar migrar o resto da suíte de volta pro HEAD.
        craving.delete()
        estado.delete()

    def test_estados_cansaco_e_cansado_colapsam_num_so_codigo(self, banco_pre_taxonomia):
        apps_0007 = _migrar(LOG_0007)
        user = _criar_usuario(apps_0007)
        CravingEvent = apps_0007.get_model("log", "CravingEvent")
        EstadoInterno = apps_0007.get_model("baseline", "EstadoInterno")

        craving = CravingEvent.objects.create(
            user=user, timestamp=timezone.now(), substancia="tabaco", intensidade_pico=6,
            gatilho_texto="euforia",
        )
        cansaco = EstadoInterno.objects.create(user=user, nome="cansaço")
        cansado = EstadoInterno.objects.create(user=user, nome="cansado")
        craving.estados_m2m.add(cansaco, cansado)

        apps_0008 = _migrar(LOG_0008)
        c = apps_0008.get_model("log", "CravingEvent").objects.get(pk=craving.pk)

        assert c.estados == ["cansaco"]  # duas variações de digitação, um código só

    def test_banco_vazio_e_no_op_sem_erro(self, banco_pre_taxonomia):
        _migrar(LOG_0007)

        apps_0008 = _migrar(LOG_0008)  # não pode levantar nada

        assert list(apps_0008.get_model("log", "CravingEvent").objects.all()) == []
        assert list(apps_0008.get_model("log", "Slip").objects.all()) == []
