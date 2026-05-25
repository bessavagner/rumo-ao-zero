"""Cálculos derivados do log (streaks, economia, eficácia de substituições).

Princípios:
- Framework §4.4: slip NÃO zera o cumulativo — é dado, não falência.
- Métricas são **derivadas dos eventos**, não de campos denormalizados, para nunca ficarem
  desatualizadas (ex.: eficácia de substituição vem dos CravingEvent, não de Substitution.eficacia_media).
- Data Zero pode estar no futuro (pré-Dia 1): nesse caso streak/economia retornam 0.
"""

from collections import Counter, defaultdict
from datetime import date, timedelta

from apps.baseline.models import Substitution

from .models import CravingEvent, DailyEntry, Slip


def dias_ate_dia1(user) -> int:
    """Dias que faltam até a Data Zero (0 se a cessação já começou)."""
    return max(0, (user.baselineprofile.data_zero - date.today()).days)


def streak_consecutivo(user, substancia: str) -> int:
    """Dias consecutivos sem slip da substância, até hoje. 0 se a cessação ainda não começou."""
    today = date.today()
    baseline = user.baselineprofile.data_zero
    if today < baseline:
        return 0
    last_slip = (
        Slip.objects.filter(user=user, substancia=substancia)
        .order_by("-timestamp")
        .first()
    )
    if last_slip and last_slip.timestamp.date() >= baseline:
        return (today - last_slip.timestamp.date()).days
    return (today - baseline).days


def streak_cumulativo_ano(user, substancia: str) -> int:
    """Dias livres acumulados no ano desde a Data Zero (slip não zera, só desconta o dia)."""
    today = date.today()
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
    dias = max(0, (date.today() - baseline.data_zero).days)
    return float(baseline.custo_mensal_estimado) * dias / 30


def substituicoes_eficacia(user) -> list[dict]:
    """Eficácia REAL das substituições, calculada dos CravingEvent (não dos campos denormalizados).

    Para cada substituição usada: nº de usos, taxa de resolução (cravings que baixaram para ≤3,
    i.e. com `tempo_para_baixar_3` registrado) e tempo médio até baixar. Ordenado por eficácia.
    """
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
    """Frequência dos estados internos (ex-HALT) nos DailyEntry + CravingEvent dos últimos N dias."""
    desde = date.today() - timedelta(days=dias)
    contagem = Counter()
    for ev in CravingEvent.objects.filter(user=user, timestamp__date__gte=desde).prefetch_related("estados"):
        for e in ev.estados.all():
            contagem[e.nome] += 1
    for de in DailyEntry.objects.filter(user=user, data__gte=desde).prefetch_related("estados"):
        for e in de.estados.all():
            contagem[e.nome] += 1
    return [{"estado": nome, "ocorrencias": n} for nome, n in contagem.most_common()]


def triggers_frequencia(user, dias: int = 30) -> list[dict]:
    """Frequência dos gatilhos nos últimos N dias, dos CravingEvent (Trigger ligado ou texto livre)."""
    desde = date.today() - timedelta(days=dias)
    contagem = Counter()
    eventos = CravingEvent.objects.filter(
        user=user, timestamp__date__gte=desde
    ).values("trigger__nome", "gatilho_texto")
    for ev in eventos:
        nome = ev["trigger__nome"] or ev["gatilho_texto"] or "(sem gatilho)"
        contagem[nome] += 1
    return [{"gatilho": nome, "ocorrencias": n} for nome, n in contagem.most_common()]
