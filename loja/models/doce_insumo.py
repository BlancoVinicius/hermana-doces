import uuid
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from .doce import Doce
from .insumo import Insumo


class DoceInsumo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doce = models.ForeignKey(
        Doce,
        on_delete=models.CASCADE,
        related_name="ingredientes",
        verbose_name="Doce",
    )
    insumo = models.ForeignKey(
        Insumo,
        on_delete=models.PROTECT,
        related_name="usado_em_doces",
        verbose_name="Insumo",
    )
    quantidade = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        verbose_name="Quantidade",
        help_text="Quantidade utilizada na unidade de medida do insumo (ex: g, ml, un)",
    )

    class Meta:
        app_label = 'loja'
        verbose_name = "Insumo do Doce"
        verbose_name_plural = "Insumos do Doce (Ficha Técnica)"
        unique_together = (('doce', 'insumo'),)  # Evita duplicar o mesmo insumo no mesmo doce


    def __str__(self):
        if not self.insumo_id or not self.doce_id:
            return "Insumo do doce"

        return (
            f"{self.quantidade} {self.insumo.unidade_medida} "
            f"de {self.insumo.nome} em {self.doce.nome}"
        )
    
    @property
    def custo_item(self) -> Decimal:
        """Calcula o custo proporcional deste insumo no doce."""
        if self.quantidade is None or self.insumo_id is None:
            return Decimal("0.00")

        if self.insumo.custo_unitario is None:
            return Decimal("0.00")

        return self.quantidade * self.insumo.custo_unitario