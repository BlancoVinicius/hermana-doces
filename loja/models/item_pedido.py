import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from .pedido import StatusPedido


class ItemPedido(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    pedido = models.ForeignKey(
        "loja.Pedido",
        on_delete=models.CASCADE,
        related_name="itens",
    )

    produto = models.ForeignKey(
        "loja.Produto",
        on_delete=models.PROTECT,
        related_name="itens_pedido",
    )

    quantidade = models.PositiveIntegerField(default=1)

    preco_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
    )

    preco_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    class Meta:
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens do Pedido"

    def save(self, *args, **kwargs):
        # Captura o preço atual somente na criação; depois preserva o preço histórico.
        if self._state.adding and self.produto_id and self.preco_unitario is None:
            self.preco_unitario = self.produto.preco
        if self.preco_unitario is not None:
            self.preco_total = self.preco_unitario * self.quantidade
        super().save(*args, **kwargs)
        self.pedido.atualizar_totais()

    def delete(self, *args, **kwargs):
        if self.pedido.status == StatusPedido.ENTREGUE or self.pedido.status == StatusPedido.CANCELADO or self.pedido.status == StatusPedido.ENVIADO:
            raise ValidationError(
                "Não é permitido excluir itens de um pedido entregue."
            )
        return super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"