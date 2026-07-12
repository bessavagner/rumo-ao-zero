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


class EstadoInterno(models.Model):
    """Estado interno que antecede o craving (ex-HALT). Catálogo EXTENSÍVEL pelo usuário.

    Seeds: fome, raiva, solidão, cansaço (os 4 do HALT). O usuário pode adicionar outros
    (frustrado, eufórico, sobrecarregado, ansioso, entediado, ...). Vazio nos logs = nenhum.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="estados")
    nome = models.CharField(max_length=64)
    descricao = models.TextField(blank=True)
    ordem = models.PositiveSmallIntegerField(default=0)
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "nome")]
        ordering = ["ordem", "nome"]
        verbose_name = "Estado"
        verbose_name_plural = "Estados"

    def __str__(self):
        return self.nome


class Trigger(models.Model):
    """Triggers Map — evolui ao longo do processo."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="triggers")
    nome = models.CharField(max_length=128)
    contexto = models.TextField(blank=True)
    emocao_precedente = models.CharField(max_length=64, blank=True)
    estado_mais_comum = models.ForeignKey(
        "EstadoInterno", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    frequencia_semana = models.PositiveSmallIntegerField(default=0)
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome


class Substitution(models.Model):
    """Banco de substituições — testadas e marcadas pela eficácia real."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="substitutions")
    nome = models.CharField(max_length=128)
    categoria = models.CharField(
        max_length=32,
        choices=[
            ("oral", "Oral (chá, água, goma)"),
            ("movimento", "Movimento (caminhar, alongar)"),
            ("social", "Social (ligar, mensagem)"),
            ("cognitivo", "Cognitivo (escrever, ler)"),
            ("ambiental", "Ambiental (mudar ambiente)"),
        ],
    )
    eficacia_media = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    vezes_usado = models.PositiveIntegerField(default=0)
    notas = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


class IfThenPlan(models.Model):
    """Implementation Intentions (Gollwitzer). "SE <situação> ENTÃO <ação>".

    A situação vem da mesma taxonomia dos cravings — é o que permite ligar um craving ao plano
    que existe para aquele gatilho. Sem `gatilhos_adicionais`: um plano responde a um gatilho.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ifthen_plans")
    gatilho_texto = models.CharField(max_length=255, blank=True)  # legado — sai na migration 0006
    trigger = models.ForeignKey(Trigger, null=True, blank=True, on_delete=models.SET_NULL)
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
