"""Etapa 1 da migração de gatilhos: o RELATÓRIO.

Lê os textos livres distintos (cravings, slips, if-thens — ou os nomes de EstadoInterno),
aplica as regras de palavra-chave da taxonomia e escreve um CSV **de proposta**. O humano revisa,
corrige, preenche os não casados, renomeia para `mapas/<alvo>.csv` e COMMITA. Só então a data
migration roda — ela não adivinha nada em tempo de execução: executa uma decisão humana que está
versionada.

Pós Task 7: os models legados (`Trigger`, `EstadoInterno`, os campos `gatilho_texto`/
`estados_m2m`) já foram apagados do código — a migração de dados real já rodou e foi verificada.
Mas o runbook de deploy manda rodar este comando **na friday, antes de migrar**, quando o banco
de produção ainda está no schema antigo. Por isso o comando não usa o ORM do Django (os models
antigos não existem mais para ler): ele abre um arquivo SQLite **pré-migração** com `sqlite3` da
stdlib, em modo somente leitura, e lê as tabelas legadas por SQL cru.

    uv run python manage.py mapear_gatilhos --banco /caminho/db.sqlite3.pre-migracao --alvo gatilhos
    uv run python manage.py mapear_gatilhos --banco /caminho/db.sqlite3.pre-migracao --alvo estados
"""

import csv
import sqlite3
from collections import Counter
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.baseline import taxonomia

CABECALHO = ["texto_original", "ocorrencias", "codigo", "regra"]
SEM_CORRESPONDENCIA = "SEM CORRESPONDENCIA"

# (tabela, coluna) que precisam existir no banco pré-migração para `--alvo gatilhos`.
TABELAS_GATILHO = [
    ("log_cravingevent", "gatilho_texto"),
    ("log_slip", "gatilho_texto"),
    ("baseline_ifthenplan", "gatilho_texto"),
]

# Modelos que têm (tiveram) o M2M para EstadoInterno. O nome da tabela de junção depende de o
# banco ser de antes ou de depois do rename `estados` -> `estados_m2m` (migração 0007 do log).
MODELOS_ESTADO_M2M = ["cravingevent", "dailyentry", "pulso"]


def _tabelas_existentes(conn: sqlite3.Connection) -> set[str]:
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return {linha[0] for linha in cur.fetchall()}


def _textos_de_gatilho(conn: sqlite3.Connection, tabelas: set[str]) -> Counter:
    contagem: Counter = Counter()
    for tabela, coluna in TABELAS_GATILHO:
        if tabela not in tabelas:
            raise CommandError(
                f"Tabela '{tabela}' não encontrada no banco informado. "
                "--banco precisa ser um arquivo SQLite PRÉ-migração (schema legado, de antes "
                "de rodar `migrate` na friday) — este arquivo não é um banco assim."
            )
        cur = conn.execute(f"SELECT {coluna} FROM {tabela}")
        for (texto,) in cur.fetchall():
            texto = (texto or "").strip()
            if texto:
                contagem[texto] += 1
    return contagem


def _tabela_juncao_estados(tabelas: set[str], modelo: str) -> str | None:
    """Nome real da tabela de junção do M2M `estados` de `modelo` neste banco específico.

    Tenta o nome pós-rename primeiro (`..._estados_m2m`) e cai para o nome legado
    (`..._estados`) se for um banco de antes da migração 0007. Devolve None se nenhum dos dois
    existir (ex.: banco de antes do model ganhar esse M2M).
    """
    for nome in (f"log_{modelo}_estados_m2m", f"log_{modelo}_estados"):
        if nome in tabelas:
            return nome
    return None


def _textos_de_estado(conn: sqlite3.Connection, tabelas: set[str]) -> Counter:
    if "baseline_estadointerno" not in tabelas:
        raise CommandError(
            "Tabela 'baseline_estadointerno' não encontrada no banco informado. "
            "--banco precisa ser um arquivo SQLite PRÉ-migração (de antes da remoção do model "
            "EstadoInterno) — este arquivo não é um banco assim."
        )
    estados = conn.execute("SELECT id, nome FROM baseline_estadointerno").fetchall()

    usos_por_id: Counter = Counter()
    achou_alguma_juncao = False
    for modelo in MODELOS_ESTADO_M2M:
        tabela_juncao = _tabela_juncao_estados(tabelas, modelo)
        if tabela_juncao is None:
            continue
        achou_alguma_juncao = True
        cur = conn.execute(
            f"SELECT estadointerno_id, COUNT(*) FROM {tabela_juncao} GROUP BY estadointerno_id"
        )
        for estado_id, n in cur.fetchall():
            usos_por_id[estado_id] += n

    contagem: Counter = Counter()
    for estado_id, nome in estados:
        nome = (nome or "").strip()
        if not nome:
            continue
        usos = usos_por_id[estado_id] if achou_alguma_juncao else 0
        contagem[nome] += max(usos, 1)  # um estado sem uso ainda precisa entrar no mapa
    return contagem


class Command(BaseCommand):
    help = (
        "Gera o CSV de proposta de mapeamento texto livre -> código da taxonomia, lendo um "
        "banco SQLite pré-migração via SQL cru (os models legados já foram apagados do código)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--banco",
            required=True,
            help=(
                "Caminho de um arquivo SQLite com o schema ANTIGO (ex.: um db.sqlite3 puxado "
                "da friday antes de rodar `migrate`). Aberto só para leitura; nunca é escrito."
            ),
        )
        parser.add_argument("--alvo", choices=["gatilhos", "estados"], default="gatilhos")
        parser.add_argument(
            "--saida", default=None,
            help="Caminho do CSV. Default: apps/baseline/mapas/<alvo>.proposto.csv",
        )

    def handle(self, *args, **opts):
        alvo = opts["alvo"]
        banco = Path(opts["banco"])
        if not banco.exists():
            raise CommandError(f"--banco: arquivo '{banco}' não existe.")

        saida = Path(opts["saida"]) if opts["saida"] else (
            taxonomia.MAPAS_DIR / f"{alvo}.proposto.csv"
        )
        saida.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(f"file:{banco}?mode=ro", uri=True)
        try:
            tabelas = _tabelas_existentes(conn)
            if alvo == "gatilhos":
                contagem = _textos_de_gatilho(conn, tabelas)
                classificar = taxonomia.classificar_gatilho
            else:
                contagem = _textos_de_estado(conn, tabelas)
                classificar = taxonomia.classificar_estado
        finally:
            conn.close()

        casados, orfaos = [], []
        for texto, n in contagem.items():
            codigo, palavra = classificar(texto)
            linha = {
                "texto_original": texto,
                "ocorrencias": n,
                "codigo": codigo or "",
                "regra": f"casou: {palavra}" if codigo else SEM_CORRESPONDENCIA,
            }
            (casados if codigo else orfaos).append(linha)

        # Não casados PRIMEIRO: se ficarem no meio, se escondem — e é neles que a revisão humana
        # é obrigatória (célula `codigo` vazia; vazio na migração = 'outro').
        orfaos.sort(key=lambda l: -l["ocorrencias"])
        casados.sort(key=lambda l: -l["ocorrencias"])
        with saida.open("w", encoding="utf-8", newline="") as f:
            escritor = csv.DictWriter(f, fieldnames=CABECALHO)
            escritor.writeheader()
            escritor.writerows(orfaos + casados)

        self.stdout.write(
            f"{len(orfaos) + len(casados)} textos distintos -> {saida}\n"
            f"  {len(orfaos)} SEM correspondência (revise primeiro; estão no topo)\n"
            f"  {len(casados)} com proposta (confira antes de aprovar)\n"
            f"Revise, corrija, renomeie para {taxonomia.MAPAS_DIR / f'{alvo}.csv'} e COMMITE."
        )
