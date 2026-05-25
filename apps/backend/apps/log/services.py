"""Cálculos derivados do log (streaks, dinheiro economizado).

Regra do framework (§4.4): slip NÃO zera o cumulativo do ano — é dado, não falência.
"""

from datetime import date

from .models import Slip


def streak_consecutivo(user, substancia: str) -> int:
    """Dias consecutivos sem slip da substância, até hoje."""
    today = date.today()
    last_slip = (
        Slip.objects.filter(user=user, substancia=substancia)
        .order_by("-timestamp")
        .first()
    )
    baseline = user.baselineprofile.data_zero
    if last_slip and last_slip.timestamp.date() >= baseline:
        return (today - last_slip.timestamp.date()).days
    return (today - baseline).days


def streak_cumulativo_ano(user, substancia: str) -> int:
    """Total de dias livres no ano corrente (slip não zera, só desconta o dia)."""
    today = date.today()
    inicio_ano = date(today.year, 1, 1)
    slips_no_ano = Slip.objects.filter(
        user=user,
        substancia=substancia,
        timestamp__date__gte=inicio_ano,
    ).count()
    dias_no_ano = (today - inicio_ano).days + 1
    return max(0, dias_no_ano - slips_no_ano)


def dinheiro_economizado(user) -> float:
    """Estimativa baseada em BaselineProfile.custo_mensal_estimado."""
    baseline = user.baselineprofile
    dias = (date.today() - baseline.data_zero).days
    return float(baseline.custo_mensal_estimado) * dias / 30
