from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class User(AbstractUser):
    """Single-user na fase atual; mantém AbstractUser para extensão futura."""

    timezone = models.CharField(max_length=64, default="America/Sao_Paulo")
    regime_trabalho = models.CharField(
        max_length=32,
        choices=[("DE", "Dedicação Exclusiva"), ("CLT", "CLT"), ("OUTRO", "Outro")],
        default="DE",
    )
    vulnerabilidade_alvo = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=3.5,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Escala 0–10. 0 = cru, 10 = impessoal.",
    )

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
