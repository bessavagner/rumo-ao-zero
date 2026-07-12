"""Etapa 1 da migração de gatilhos: o RELATÓRIO.

Lê os textos livres distintos (cravings, slips, if-thens — ou os nomes de EstadoInterno),
aplica as regras de palavra-chave da taxonomia e escreve um CSV **de proposta**. O humano revisa,
corrige, preenche os não casados, renomeia para `mapas/<alvo>.csv` e COMMITA. Só então a data
migration roda — ela não adivinha nada em tempo de execução: executa uma decisão humana que está
versionada.

    uv run python manage.py mapear_gatilhos --alvo gatilhos
    uv run python manage.py mapear_gatilhos --alvo estados
"""

import csv
from collections import Counter
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.baseline import taxonomia

CABECALHO = ["texto_original", "ocorrencias", "codigo", "regra"]
SEM_CORRESPONDENCIA = "SEM CORRESPONDENCIA"


def _textos_de_gatilho() -> Counter:
    from apps.baseline.models import IfThenPlan
    from apps.log.models import CravingEvent, Slip

    contagem: Counter = Counter()
    for model in (CravingEvent, Slip, IfThenPlan):
        for texto in model.objects.values_list("gatilho_texto", flat=True):
            if (texto or "").strip():
                contagem[texto.strip()] += 1
    return contagem


def _textos_de_estado() -> Counter:
    from apps.baseline.models import EstadoInterno

    contagem: Counter = Counter()
    for estado in EstadoInterno.objects.all():
        usos = (
            estado.cravings.count() + estado.daily_entries.count() + estado.pulsos.count()
        )
        contagem[estado.nome.strip()] += max(usos, 1)  # um estado sem uso ainda precisa de mapa
    return contagem


class Command(BaseCommand):
    help = "Gera o CSV de proposta de mapeamento texto livre -> código da taxonomia."

    def add_arguments(self, parser):
        parser.add_argument("--alvo", choices=["gatilhos", "estados"], default="gatilhos")
        parser.add_argument(
            "--saida", default=None,
            help="Caminho do CSV. Default: apps/baseline/mapas/<alvo>.proposto.csv",
        )

    def handle(self, *args, **opts):
        alvo = opts["alvo"]
        saida = Path(opts["saida"]) if opts["saida"] else (
            taxonomia.MAPAS_DIR / f"{alvo}.proposto.csv"
        )
        saida.parent.mkdir(parents=True, exist_ok=True)

        if alvo == "gatilhos":
            contagem = _textos_de_gatilho()
            classificar = taxonomia.classificar_gatilho
        else:
            contagem = _textos_de_estado()
            classificar = taxonomia.classificar_estado

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
