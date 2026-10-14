from django.db import models
from loja.models.kit import Kit
from loja.models.produto import Produto

class ItemKit(models.Model):
    kit = models.ForeignKey(
        Kit,
        on_delete=models.CASCADE,
        related_name="itens"
    )

    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name="itens_de_kit"
    )

    quantidade = models.PositiveIntegerField()

    class Meta:
        unique_together = ("kit", "produto")

    def __str__(self):
        return f"{self.quantidade}x {self.produto}"

    @property
    def custo_item(self):
        return self.produto.preco * self.quantidade 