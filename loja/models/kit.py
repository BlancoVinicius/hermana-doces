import uuid
from decimal import Decimal
from django.db import models

from .produto import Produto

class Kit(Produto):
    produtos = models.ManyToManyField(
        'loja.Produto',
        through='loja.ItemKit',
        related_name='kits',
        blank=True,
    )

    class Meta:
        app_label = 'loja'
        verbose_name = "Kit"
        verbose_name_plural = "Kits"

    def __str__(self):
        return f"Kit: {self.nome}"

    @property
    def custo_producao_total(self) -> Decimal:
        """Calcula o custo total de fabricação do kit com base nos produtos cadastrados."""
        total = Decimal('0.0000')
        for item in self.itens.all():
            total += item.custo_item
        return round(total, 2)
