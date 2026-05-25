from django.conf import settings
from django.db import models

from apps.baseline.models import Substitution, Trigger


class DailyEntry(models.Model):
    """Entrada diária de 2 min — 1 por dia por usuário."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="daily_entries")
    data = models.DateField()

    # Numéricos
    humor = models.PositiveSmallIntegerField(help_text="1–5")
    energia = models.PositiveSmallIntegerField(help_text="1–5")
    sono_h = models.DecimalField(max_digits=3, decimal_places=1)
    sono_q = models.PositiveSmallIntegerField(help_text="1–5")
    craving_pico = models.PositiveSmallIntegerField(help_text="0–10", default=0)

    # Estado interno (ex-HALT) — catálogo extensível; vazio = nenhum estado marcado
    estados = models.ManyToManyField("baseline.EstadoInterno", blank=True, related_name="daily_entries")

    # Substituições usadas hoje
    substituicoes = models.ManyToManyField(Substitution, blank=True)

    # Prosa curta (3 linhas + 2 micro-blocos)
    linha_1 = models.CharField(max_length=255, blank=True)
    linha_2 = models.CharField(max_length=255, blank=True)
    linha_3 = models.CharField(max_length=255, blank=True)
    algo_do_corpo = models.CharField(max_length=255, blank=True)
    coisa_boa = models.CharField(max_length=255, blank=True)
    coisa_dificil = models.CharField(max_length=255, blank=True)

    # Flags do dia
    estado_checado = models.BooleanField(default=False)
    cravings_logados = models.BooleanField(default=False)

    # Editorial
    publicable = models.BooleanField(default=False)
    publicable_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("user", "data")]
        ordering = ["-data"]
        indexes = [models.Index(fields=["user", "-data"])]

    def __str__(self):
        return f"Diário {self.data} ({self.user})"


class CravingEvent(models.Model):
    """Evento de craving ≥ 6/10 — pode haver vários por dia."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cravings")
    timestamp = models.DateTimeField()

    SUBSTANCIA = [("alcool", "Álcool"), ("tabaco", "Tabaco"), ("ambos", "Ambos")]
    substancia = models.CharField(max_length=8, choices=SUBSTANCIA)

    intensidade_pico = models.PositiveSmallIntegerField(help_text="0–10")
    duracao_min = models.PositiveSmallIntegerField(default=0)
    intensidade_final = models.PositiveSmallIntegerField(help_text="0–10", default=0)
    tempo_para_baixar_3 = models.PositiveSmallIntegerField(null=True, blank=True, help_text="min até ≤3")

    gatilho_texto = models.CharField(max_length=255)
    trigger = models.ForeignKey(Trigger, null=True, blank=True, on_delete=models.SET_NULL)
    estados = models.ManyToManyField("baseline.EstadoInterno", blank=True, related_name="cravings")

    # Thought record 7 colunas (parcial)
    pensamento_automatico = models.TextField(blank=True)
    evidencia_favor = models.TextField(blank=True)
    evidencia_contra = models.TextField(blank=True)
    pensamento_balanceado = models.TextField(blank=True)

    # Resposta
    substituicao_usada = models.ForeignKey(Substitution, null=True, blank=True, on_delete=models.SET_NULL)
    aprendizado = models.CharField(max_length=255, blank=True)

    # If-then gerado a partir deste evento (opcional)
    if_then_gerado = models.ForeignKey(
        "baseline.IfThenPlan",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="evento_origem",
    )

    publicable = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [models.Index(fields=["user", "-timestamp"])]

    def __str__(self):
        return f"Craving {self.substancia} {self.timestamp:%Y-%m-%d %H:%M}"


class Slip(models.Model):
    """Slip registrado como DADO — sem julgamento."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="slips")
    timestamp = models.DateTimeField()

    SUBSTANCIA = [("alcool", "Álcool"), ("tabaco", "Tabaco")]
    substancia = models.CharField(max_length=8, choices=SUBSTANCIA)

    quantidade = models.CharField(max_length=64, blank=True, help_text="ex: 2 cervejas, 3 cigarros")
    contexto = models.TextField(blank=True)
    gatilho_texto = models.CharField(max_length=255, blank=True)
    trigger = models.ForeignKey(Trigger, null=True, blank=True, on_delete=models.SET_NULL)
    aprendizado = models.TextField(blank=True)

    # Reinício parcial: pode resetar só uma substância
    reset_streak_alcool = models.BooleanField(default=False)
    reset_streak_tabaco = models.BooleanField(default=False)

    # Cooldown editorial: bloqueia publicação relacionada por N dias
    cooldown_publicacao_ate = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"Slip {self.substancia} {self.timestamp:%Y-%m-%d}"
