from django.db import models

# Create your models here.
import uuid
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class UnidadeMedida(models.TextChoices):
    GRAMA = 'g', 'Gramas (g)'
    QUILO = 'kg', 'Quilogramas (kg)'
    MILILITRO = 'ml', 'Mililitros (ml)'
    LITRO = 'l', 'Litros (l)'
    UNIDADE = 'un', 'Unidade (un)'


class Insumo(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    nome = models.CharField(max_length=150, verbose_name="Nome do Insumo")
    unidade_medida = models.CharField(
        max_length=5,
        choices=UnidadeMedida.choices,
        default=UnidadeMedida.GRAMA,
        verbose_name="Unidade de Medida",
    )
    custo_unitario = models.DecimalField(
        max_length=10,
        decimal_places=4,
        max_digits=10,
        validators=[MinValueValidator(Decimal('0.0000'))],
        verbose_name="Custo Unitário (R$)",
        help_text="Custo por unidade de medida (ex: custo por grama ou por ml)",
    )

    # --- Controle de Estoque ---
    estoque_atual = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal('0.000'),
        validators=[MinValueValidator(Decimal('0.000'))],
        verbose_name="Estoque Atual",
    )
    estoque_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal('0.000'),
        validators=[MinValueValidator(Decimal('0.000'))],
        verbose_name="Estoque Mínimo Alerta",
        help_text="Quantidade mínima para emitir alerta de reposição",
    )

    # --- Auditoria ---
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Insumo"
        verbose_name_plural = "Insumos"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.estoque_atual} {self.unidade_medida})"

    # --- Propriedades e Métodos Úteis ---
    @property
    def precisa_reposicao(self) -> bool:
        """Indica se o estoque atual atingiu ou ficou abaixo do nível mínimo."""
        return self.estoque_atual <= self.estoque_minimo

    def dar_baixa_estoque(self, quantidade: Decimal):
        """Reduz a quantidade do estoque garantindo que não fique negativo."""
        if quantidade <= 0:
            raise ValidationError("A quantidade para baixa deve ser maior que zero.")
        if self.estoque_atual < quantidade:
            raise ValidationError(
                f"Estoque insuficiente de {self.nome}. Disponível: {self.estoque_atual}, solicitado: {quantidade}"
            )
        self.estoque_atual -= quantidade
        self.save(update_fields=["estoque_atual", "atualizado_em"])

    def adicionar_estoque(self, quantidade: Decimal, novo_custo_unitario: Decimal = None):
        """Adiciona estoque e opcionalmente atualiza o custo unitário."""
        if quantidade <= 0:
            raise ValidationError("A quantidade adicionada deve ser maior que zero.")
        self.estoque_atual += quantidade
        if novo_custo_unitario is not None and novo_custo_unitario >= 0:
            self.custo_unitario = novo_custo_unitario
        self.save(update_fields=["estoque_atual", "custo_unitario", "atualizado_em"])