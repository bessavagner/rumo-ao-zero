"""Cálculos derivados do log (streaks, economia, eficácia de substituições).

Princípios:
- Framework §4.4: slip NÃO zera o cumulativo — é dado, não falência.
- Métricas são **derivadas dos eventos**, não de campos denormalizados, para nunca ficarem
  desatualizadas (ex.: eficácia de substituição vem dos CravingEvent, não de Substitution.eficacia_media).
- Data Zero pode estar no futuro (pré-Dia 1): nesse caso streak/economia retornam 0.
"""

from collections import Counter, defaultdict
from datetime import date, timedelta

from django.utils import timezone

from apps.baseline.taxonomia import categoria_de, rotulo_categoria, rotulo_estado, rotulo_situacao

from .models import CravingEvent, DailyEntry, Slip


def dias_ate_dia1(user) -> int:
    """Dias que faltam até a Data Zero (0 se a cessação já começou)."""
    return max(0, (user.baselineprofile.data_zero - timezone.localdate()).days)


def streak_consecutivo(user, substancia: str) -> int:
    """Dias consecutivos sem slip da substância, até hoje. 0 se a cessação ainda não começou."""
    today = timezone.localdate()
    baseline = user.baselineprofile.data_zero
    if today < baseline:
        return 0
    last_slip = (
        Slip.objects.filter(user=user, substancia=substancia)
        .order_by("-timestamp")
        .first()
    )
    if last_slip:
        # timestamp é UTC-aware; converte pro fuso local antes de extrair a data,
        # senão mistura data local (today) com data UTC e dá off-by-one perto da meia-noite.
        slip_date = timezone.localtime(last_slip.timestamp).date()
        if slip_date >= baseline:
            return (today - slip_date).days
    return (today - baseline).days


def streak_cumulativo_ano(user, substancia: str) -> int:
    """Dias livres acumulados no ano desde a Data Zero (slip não zera, só desconta o dia)."""
    today = timezone.localdate()
    baseline = user.baselineprofile.data_zero
    inicio = max(date(today.year, 1, 1), baseline)
    if today < inicio:
        return 0
    slips = Slip.objects.filter(
        user=user, substancia=substancia, timestamp__date__gte=inicio
    ).count()
    dias = (today - inicio).days + 1
    return max(0, dias - slips)


def dinheiro_economizado(user) -> float:
    """Estimativa por BaselineProfile.custo_mensal_estimado (0 antes da Data Zero)."""
    baseline = user.baselineprofile
    dias = max(0, (timezone.localdate() - baseline.data_zero).days)
    return float(baseline.custo_mensal_estimado) * dias / 30


def substituicoes_eficacia(user) -> list[dict]:
    """Eficácia REAL das substituições, calculada dos CravingEvent (não dos campos denormalizados).

    Para cada substituição usada: nº de usos, taxa de resolução (cravings que baixaram para ≤3,
    i.e. com `tempo_para_baixar_3` registrado) e tempo médio até baixar. Ordenado por eficácia.
    """
    # NOTA (Task 6): `substituicao_usada` e `Substitution` saíram do model nesta task — esta
    # função ainda referencia o catálogo antigo e vai quebrar em runtime. Conserto é a Task 7
    # (reescrever para a taxonomia fixa). Import local só para não derrubar o módulo inteiro
    # (e com ele config/urls.py) por causa de uma função que ninguém mais chama sem quebrar.
    from apps.baseline.models import Substitution

    stats = defaultdict(lambda: {"usos": 0, "resolvidos": 0, "soma_tempo": 0})
    eventos = CravingEvent.objects.filter(
        user=user, substituicao_usada__isnull=False
    ).values("substituicao_usada", "tempo_para_baixar_3")
    for ev in eventos:
        s = stats[ev["substituicao_usada"]]
        s["usos"] += 1
        if ev["tempo_para_baixar_3"] is not None:
            s["resolvidos"] += 1
            s["soma_tempo"] += ev["tempo_para_baixar_3"]
    nomes = dict(Substitution.objects.filter(user=user).values_list("id", "nome"))
    resultado = []
    for sid, s in stats.items():
        taxa = s["resolvidos"] / s["usos"] if s["usos"] else 0
        tempo_medio = s["soma_tempo"] / s["resolvidos"] if s["resolvidos"] else None
        resultado.append({
            "substituicao": nomes.get(sid, f"#{sid}"),
            "usos": s["usos"],
            "taxa_resolucao": round(taxa, 2),
            "tempo_medio_min": round(tempo_medio, 1) if tempo_medio is not None else None,
        })
    resultado.sort(key=lambda d: (d["taxa_resolucao"], d["usos"]), reverse=True)
    return resultado


def estados_frequencia(user, dias: int = 30) -> list[dict]:
    """Frequência dos estados internos (ex-HALT) nos DailyEntry + CravingEvent dos últimos N dias.

    Códigos da taxonomia fixa: 'cansaço' e 'cansado' não podem mais coexistir como dois estados.
    """
    desde = timezone.localdate() - timedelta(days=dias)
    contagem = Counter()
    for codigos in CravingEvent.objects.filter(
        user=user, timestamp__date__gte=desde
    ).values_list("estados", flat=True):
        contagem.update(codigos or [])
    for codigos in DailyEntry.objects.filter(
        user=user, data__gte=desde
    ).values_list("estados", flat=True):
        contagem.update(codigos or [])
    return [
        {"estado": c, "rotulo": rotulo_estado(c), "ocorrencias": n}
        for c, n in contagem.most_common()
    ]


def triggers_frequencia(user, dias: int = 30) -> dict:
    """Três cortes dos gatilhos dos CravingEvent dos últimos N dias.

    1. `por_situacao` — SÓ o gatilho principal (são as barras do dashboard). Um craving com 4
       gatilhos soma 1, não 4: senão "qual é o meu pior gatilho" volta a mentir.
    2. `por_categoria` — a lente do IDS/ISS. 'outro' não tem categoria e não entra.
    3. `coocorrencia` — quais adicionais aparecem junto de cada principal ("tédio quase sempre
       vem junto com cansaço").

    Agrega em Python de propósito: o SQLite não indexa JSONField, e a escala aqui é de algumas
    centenas de eventos de um usuário só — o resto do services.py já agrega em Python por design.
    """
    desde = timezone.localdate() - timedelta(days=dias)
    por_situacao = Counter()
    por_categoria = Counter()
    coocorrencia = Counter()

    eventos = CravingEvent.objects.filter(user=user, timestamp__date__gte=desde).values(
        "gatilho", "gatilhos_adicionais"
    )
    for ev in eventos:
        principal = ev["gatilho"] or "outro"
        por_situacao[principal] += 1
        categoria = categoria_de(principal)
        if categoria:
            por_categoria[categoria] += 1
        for adicional in ev["gatilhos_adicionais"] or []:
            if adicional != principal:
                coocorrencia[(principal, adicional)] += 1

    return {
        "por_situacao": [
            {"situacao": c, "rotulo": rotulo_situacao(c), "ocorrencias": n}
            for c, n in por_situacao.most_common()
        ],
        "por_categoria": [
            {"categoria": c, "rotulo": rotulo_categoria(c), "ocorrencias": n}
            for c, n in por_categoria.most_common()
        ],
        "coocorrencia": [
            {
                "situacao": p, "rotulo": rotulo_situacao(p),
                "adicional": a, "rotulo_adicional": rotulo_situacao(a),
                "ocorrencias": n,
            }
            for (p, a), n in coocorrencia.most_common()
        ],
    }
