import uuid
from decimal import Decimal

from django.db.models import Sum

from django.core.validators import MinValueValidator
from django.db import models


class StatusPedido(models.TextChoices):
    ORCAMENTO = "ORCAMENTO", "Orçamento"
    PENDENTE = "PENDENTE", "Pendente"
    PAGO = "PAGO", "Pago"
    EM_PRODUCAO = "EM_PRODUCAO", "Em Produção"
    PRONTO = "PRONTO", "Pronto"
    ENVIADO = "ENVIADO", "Enviado"
    ENTREGUE = "ENTREGUE", "Entregue"
    CANCELADO = "CANCELADO", "Cancelado"
    # AGUARDANDO_PAGAMENTO = "AGUARDANDO_PAGAMENTO", "Aguardando Pagamento"


class Pedido(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    cliente = models.ForeignKey(
        "loja.Cliente",
        on_delete=models.PROTECT,
        related_name="pedidos",
        verbose_name="Cliente",
    )

    endereco_entrega = models.ForeignKey(
        "loja.Endereco",
        on_delete=models.PROTECT,
        related_name="pedidos",
        verbose_name="Endereço de Entrega",
    )

    status = models.CharField(
        max_length=30,
        choices=StatusPedido.choices,
        default=StatusPedido.ORCAMENTO,
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    frete = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    desconto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ["-criado_em"]

    @property
    def total_pago(self):
        pagamento = getattr(self, "pagamento", None)
        if pagamento and pagamento.status == "APROVADO":
            return pagamento.valor
        return Decimal("0.00")

    @property
    def saldo_devedor(self):
        return max(self.total - self.total_pago, Decimal("0.00"))

    @property
    def numero(self):
        return str(self.pk).split("-")[0].upper()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("loja:pedido_detalhe", kwargs={"pk": self.pk})

    def atualizar_totais(self, *, salvar=True):
        if not self.pk:
            return
        subtotal = self.itens.aggregate(total=Sum("preco_total"))["total"] or Decimal("0.00")
        self.subtotal = subtotal
        self.total = max(subtotal + self.frete - self.desconto, Decimal("0.00"))
        if salvar:
            self.save(update_fields=["subtotal", "total", "atualizado_em"])

    def __str__(self):
        return f"Pedido #{str(self.id)[:8]}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
