from decimal import Decimal
from django.db import models
from .produto import Produto


class Doce(Produto):
    insumos = models.ManyToManyField(
        'loja.Insumo',
        through='loja.DoceInsumo',
        related_name='doces',
        blank=True,
    )

    class Meta:
        app_label = 'loja'
        verbose_name = "Doce"
        verbose_name_plural = "Doces"

    @property
    def custo_producao_total(self) -> Decimal:
        """Calcula o custo total de fabricação do doce com base nos insumos cadastrados."""
        total = Decimal('0.0000')
        for item in self.ingredientes.all():
            total += item.custo_item
        return round(total, 2)