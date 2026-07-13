from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.baseline.taxonomia import SITUACOES, SUBSTITUICOES, categoria_de, valida_estados, valida_situacoes

# Escalas subjetivas — unificadas em 0–10 (antes humor/energia/sono_q eram 1–5). Validadas no backend.
ESCALA_0_10 = [MinValueValidator(0), MaxValueValidator(10)]


class DailyEntry(models.Model):
    """Entrada diária de 2 min — 1 por dia por usuário."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="daily_entries")
    data = models.DateField()

    # Numéricos
    humor = models.PositiveSmallIntegerField(help_text="0–10", validators=ESCALA_0_10)
    energia = models.PositiveSmallIntegerField(help_text="0–10", validators=ESCALA_0_10)
    sono_h = models.DecimalField(max_digits=3, decimal_places=1)
    sono_q = models.PositiveSmallIntegerField(help_text="0–10", validators=ESCALA_0_10)
    craving_pico = models.PositiveSmallIntegerField(help_text="0–10", default=0, validators=ESCALA_0_10)

    # Estado interno (ex-HALT) — códigos da taxonomia fixa; lista vazia = nenhum estado marcado.
    estados = models.JSONField(default=list, blank=True, validators=[valida_estados])

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

    intensidade_pico = models.PositiveSmallIntegerField(help_text="0–10", validators=ESCALA_0_10)
    duracao_min = models.PositiveSmallIntegerField(default=0)
    intensidade_final = models.PositiveSmallIntegerField(help_text="0–10", default=0, validators=ESCALA_0_10)
    tempo_para_baixar_3 = models.PositiveSmallIntegerField(null=True, blank=True, help_text="min até ≤3")

    # Gatilho: taxonomia fixa. O principal é o que conta nas barras do dashboard (um craving com
    # 4 gatilhos não pode somar em 4 barras e distorcer "qual é o meu pior gatilho"); os
    # adicionais alimentam a análise de co-ocorrência.
    gatilho = models.CharField(max_length=32, choices=SITUACOES)
    gatilhos_adicionais = models.JSONField(default=list, blank=True, validators=[valida_situacoes])
    detalhes = models.TextField(blank=True, help_text="O texto livre — opcional.")
    estados = models.JSONField(default=list, blank=True, validators=[valida_estados])

    # Thought record 7 colunas (parcial)
    pensamento_automatico = models.TextField(blank=True)
    evidencia_favor = models.TextField(blank=True)
    evidencia_contra = models.TextField(blank=True)
    pensamento_balanceado = models.TextField(blank=True)

    # Resposta
    # A substituição é uma das 5 categorias fixas de enfrentamento (taxonomia). O que a pessoa fez
    # de fato ("corri 5k") vai em `substituicao_detalhes` — preservado, mas não contado. Vazio ("")
    # significa "nada / não registrei", e é por isso que não existe categoria "outro".
    substituicao = models.CharField(max_length=16, choices=SUBSTITUICOES, blank=True)
    substituicao_detalhes = models.TextField(blank=True, help_text="O que fiz, nas minhas palavras.")
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

    @property
    def categoria(self) -> str | None:
        """Categoria clínica (IDS/ISS) derivada da situação. Nunca armazenada — nunca diverge."""
        return categoria_de(self.gatilho)

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
    gatilho = models.CharField(max_length=32, choices=SITUACOES)
    gatilhos_adicionais = models.JSONField(default=list, blank=True, validators=[valida_situacoes])
    detalhes = models.TextField(blank=True, help_text="O texto livre — opcional.")
    estados = models.JSONField(default=list, blank=True, validators=[valida_estados])
    aprendizado = models.TextField(blank=True)

    # Reinício parcial: pode resetar só uma substância
    reset_streak_alcool = models.BooleanField(default=False)
    reset_streak_tabaco = models.BooleanField(default=False)

    # Cooldown editorial: bloqueia publicação relacionada por N dias
    cooldown_publicacao_ate = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    @property
    def categoria(self) -> str | None:
        """Categoria clínica (IDS/ISS) derivada da situação. Nunca armazenada — nunca diverge."""
        return categoria_de(self.gatilho)

    def __str__(self):
        return f"Slip {self.substancia} {self.timestamp:%Y-%m-%d}"


class Pulso(models.Model):
    """Check-in de humor/energia AO LONGO DO DIA — vários por dia.

    Complementa o ``DailyEntry`` (reflexão de fim de dia, 1×/dia): o Pulso é a **amostra do
    momento**. Humor e energia oscilam intra-dia; capturar a série temporal permite ver a
    curva do dia e cruzá-la com o timing dos cravings (ex.: "o craving bate quando o humor
    cai no fim da tarde"). Mobile-first, baixa fricção: só humor + energia são obrigatórios.
    Decisão: D-002.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pulsos")
    timestamp = models.DateTimeField()

    humor = models.PositiveSmallIntegerField(help_text="0–10", validators=ESCALA_0_10)
    energia = models.PositiveSmallIntegerField(help_text="0–10", validators=ESCALA_0_10)
    craving = models.PositiveSmallIntegerField(help_text="0–10", default=0, validators=ESCALA_0_10)

    # Mesmo catálogo ex-HALT do DailyEntry/CravingEvent; vazio = nenhum estado marcado.
    estados = models.JSONField(default=list, blank=True, validators=[valida_estados])
    nota = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [models.Index(fields=["user", "-timestamp"])]

    def __str__(self):
        return f"Pulso {self.timestamp:%Y-%m-%d %H:%M} (humor {self.humor})"
