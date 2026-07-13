from django.conf import settings
from django.db import models

from apps.baseline.taxonomia import SITUACOES, categoria_de


class BaselineProfile(models.Model):
    """Snapshot do Dia 0 — preenchido uma vez, raramente editado."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    data_zero = models.DateField(help_text="Data marcada como Dia 1.")
    cigarros_dia_anterior = models.IntegerField(default=0)
    drinks_semana_anterior = models.IntegerField(default=0)
    custo_mensal_estimado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    carta_ancora = models.TextField(blank=True, help_text="Para o eu de daqui a 30 dias, em crise.")
    motivacoes_desire = models.TextField(blank=True)
    motivacoes_ability = models.TextField(blank=True)
    motivacoes_reasons = models.TextField(blank=True)
    motivacoes_need = models.TextField(blank=True)
    commitment_statement = models.TextField(blank=True)
    baseline_peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    baseline_circ_abdominal = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, help_text="cm; jejum, pós-banheiro"
    )
    baseline_pa = models.CharField(max_length=16, blank=True, help_text="ex: 120/80")
    baseline_hr_repouso = models.IntegerField(null=True, blank=True)
    # Pennebaker (cifragem at-rest adiada — ver spec §1)
    pennebaker_dia1 = models.TextField(blank=True)
    pennebaker_dia2 = models.TextField(blank=True)
    pennebaker_dia3 = models.TextField(blank=True)
    pennebaker_dia4 = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Baseline {self.user} (Dia 1 = {self.data_zero})"


class Value(models.Model):
    """Hierarchy of Values — 5 valores núcleo."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="values")
    ordem = models.PositiveSmallIntegerField()
    nome = models.CharField(max_length=64)
    como_afeta_uso = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["ordem"]
        unique_together = [("user", "ordem")]

    def __str__(self):
        return self.nome


class IfThenPlan(models.Model):
    """Implementation Intentions (Gollwitzer). "SE <situação> ENTÃO <ação>".

    A situação vem da mesma taxonomia dos cravings — é o que permite ligar um craving ao plano
    que existe para aquele gatilho. Sem `gatilhos_adicionais`: um plano responde a um gatilho.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ifthen_plans")
    gatilho = models.CharField(max_length=32, choices=SITUACOES)
    detalhes = models.TextField(blank=True)
    acao = models.TextField()
    ativo = models.BooleanField(default=True)
    vezes_acionado = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def categoria(self) -> str | None:
        return categoria_de(self.gatilho)

    def __str__(self):
        return f"SE {self.gatilho}"
