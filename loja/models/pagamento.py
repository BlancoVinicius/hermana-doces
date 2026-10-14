import uuid
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class MetodoPagamento(models.TextChoices):
    PIX = "PIX", "PIX"
    CARTAO_CREDITO = "CARTAO_CREDITO", "Cartão de Crédito"
    CARTAO_DEBITO = "CARTAO_DEBITO", "Cartão de Débito"
    DINHEIRO = "DINHEIRO", "Dinheiro"
    TRANSFERENCIA = "TRANSFERENCIA", "Transferência"


class StatusPagamento(models.TextChoices):
    PENDENTE = "PENDENTE", "Pendente"
    APROVADO = "APROVADO", "Aprovado"
    CANCELADO = "CANCELADO", "Cancelado"
    ESTORNADO = "ESTORNADO", "Estornado"


class Pagamento(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    pedido = models.OneToOneField(
        "loja.Pedido",
        on_delete=models.CASCADE,
        related_name="pagamento",
    )

    status = models.CharField(
        max_length=20,
        choices=StatusPagamento.choices,
        default=StatusPagamento.PENDENTE,
    )

    metodo = models.CharField(
        max_length=30,
        choices=MetodoPagamento.choices,
    )

    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    transacao_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID da Transação",
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.metodo} - R$ {self.valor}"