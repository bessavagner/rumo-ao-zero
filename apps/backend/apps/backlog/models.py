"""Backlog do projeto como dado (substitui o tracking em Obsidian).

Schema derivado de docs/.ai/reports/002_backlog/001_estrutura_obsidian.md §2.
"""

from django.conf import settings
from django.db import models

SECAO_CHOICES = [
    ("decisoes", "Decisões"),
    ("saude", "Saúde"),
    ("familia", "Família"),
    ("dedicacao_exclusiva", "Dedicação exclusiva"),
    ("identidade_digital", "Identidade digital"),
    ("captura", "Captura"),
    ("producao", "Produção"),
    ("ambiente", "Ambiente"),
    ("dia_zero", "Dia zero"),
    ("conteudo", "Conteúdo"),
    ("metricas", "Métricas"),
    ("suporte", "Suporte"),
    ("filosofia", "Filosofia"),
]
PRIORIDADE_CHOICES = [("alta", "Alta"), ("media", "Média"), ("baixa", "Baixa")]
STATUS_CHOICES = [
    ("pendente", "Pendente"),
    ("em_andamento", "Em andamento"),
    ("aguardando", "Aguardando"),
    ("bloqueado", "Bloqueado"),
    ("concluido", "Concluído"),
    ("adiado", "Adiado"),
    ("descartado", "Descartado"),
]
RESPONSAVEL_CHOICES = [
    ("eu", "Eu"),
    ("eu+esposa", "Eu + esposa"),
    ("medico", "Médico"),
    ("rh", "RH"),
    ("terapeuta", "Terapeuta"),
]


class BacklogItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="backlog_items")
    id_externo = models.CharField(max_length=16, help_text='Identificador do backlog, ex: "1.1.1"')
    titulo = models.CharField(max_length=255)
    secao = models.CharField(max_length=32, choices=SECAO_CHOICES)
    prioridade = models.CharField(max_length=8, choices=PRIORIDADE_CHOICES, default="media")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pendente")
    responsavel = models.CharField(max_length=16, choices=RESPONSAVEL_CHOICES, default="eu")

    # bloqueado_por (este item depende dos itens em blocked_by);
    # reverso .blocks == bloqueador_para
    blocked_by = models.ManyToManyField("self", symmetrical=False, blank=True, related_name="blocks")

    custo_estimado_brl = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    custo_real_brl = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    prazo_alvo = models.DateField(null=True, blank=True)
    data_inicio = models.DateField(null=True, blank=True)
    data_conclusao = models.DateField(null=True, blank=True)

    tags = models.JSONField(default=list, blank=True)
    contexto = models.TextField(blank=True)
    criterio_pronto = models.JSONField(default=list, blank=True, help_text="lista de {texto, done}")
    decisao = models.TextField(blank=True)
    notas = models.TextField(blank=True)
    historico = models.JSONField(default=list, blank=True, help_text="lista de {ts, evento}")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("user", "id_externo")]
        ordering = ["id_externo"]

    def __str__(self):
        return f"{self.id_externo} — {self.titulo}"


class Decision(models.Model):
    """ADR — registro de decisão fechada."""

    REVERSIBILIDADE = [("alta", "Alta"), ("media", "Média"), ("baixa", "Baixa")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="decisions")
    id_externo = models.CharField(max_length=16, help_text='ex: "D-001"')
    titulo = models.CharField(max_length=255)
    status = models.CharField(max_length=24, default="aceita")
    data = models.DateField()
    contexto = models.TextField(blank=True)
    opcoes = models.JSONField(default=list, blank=True, help_text="opções consideradas")
    decisao = models.TextField(blank=True)
    consequencias_positivas = models.TextField(blank=True)
    consequencias_negativas = models.TextField(blank=True)
    reversibilidade = models.CharField(max_length=8, choices=REVERSIBILIDADE, blank=True)
    quando_revisitar = models.TextField(blank=True)
    relacionada_a = models.ManyToManyField(BacklogItem, blank=True, related_name="decisions")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("user", "id_externo")]
        ordering = ["-data"]

    def __str__(self):
        return f"{self.id_externo} — {self.titulo}"


class Consulta(models.Model):
    """Registro de consulta médica/terapia."""

    ESPECIALIDADE = [
        ("psiquiatra", "Psiquiatra"),
        ("clinico", "Clínico"),
        ("terapia", "Terapia"),
        ("clinica_canabis", "Clínica canabis"),
        ("outro", "Outro"),
    ]
    MODALIDADE = [("presencial", "Presencial"), ("tele", "Teleconsulta"), ("hibrido", "Híbrido")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="consultas")
    profissional = models.CharField(max_length=128, blank=True)
    especialidade = models.CharField(max_length=24, choices=ESPECIALIDADE)
    data = models.DateField()
    modalidade = models.CharField(max_length=12, choices=MODALIDADE, default="tele")
    custo_brl = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    proxima_data = models.DateField(null=True, blank=True)
    pauta = models.TextField(blank=True)
    anamnese = models.TextField(blank=True)
    conduta = models.TextField(blank=True)
    decisoes = models.TextField(blank=True)
    proximos_passos = models.JSONField(default=list, blank=True, help_text="lista de {texto, done}")
    itens_impactados = models.ManyToManyField(BacklogItem, blank=True, related_name="consultas")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data"]

    def __str__(self):
        return f"Consulta {self.especialidade} — {self.data}"


class Compra(models.Model):
    CATEGORIA = [
        ("medicamento", "Medicamento"),
        ("equipamento", "Equipamento"),
        ("livro", "Livro"),
        ("substituicao", "Substituição"),
        ("software", "Software"),
        ("outro", "Outro"),
    ]
    STATUS = [
        ("pendente", "Pendente"),
        ("pedido", "Pedido"),
        ("recebido", "Recebido"),
        ("cancelado", "Cancelado"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="compras")
    item = models.CharField(max_length=255)
    categoria = models.CharField(max_length=16, choices=CATEGORIA)
    fornecedor = models.CharField(max_length=128, blank=True)
    preco_brl = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=12, choices=STATUS, default="pendente")
    data_pedido = models.DateField(null=True, blank=True)
    data_recebimento = models.DateField(null=True, blank=True)
    justificativa = models.TextField(blank=True)
    itens_atendidos = models.ManyToManyField(BacklogItem, blank=True, related_name="compras")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.item} ({self.categoria})"
