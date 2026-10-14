import uuid
from django.db import models
from polymorphic.models import PolymorphicModel, PolymorphicModelBase
from abc import ABCMeta, abstractmethod
from decimal import Decimal
from django.core.validators import MinValueValidator


class Categoria(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    descricao = models.TextField(blank=True, null=True)
    ordem = models.IntegerField(default=0)
    ativa = models.BooleanField(default=True)

    class Meta:
        app_label = 'loja'
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.nome

# class PolymorphicABCMeta(PolymorphicModelBase, ABCMeta):
#     pass

class Produto(PolymorphicModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="produtos",
        verbose_name="Categoria",
    )
    nome = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    descricao = models.TextField(blank=True, null=True)
    descricao_curta = models.CharField(max_length=255, blank=True, null=True)
    preco = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    destaque = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)
    peso_kg = models.DecimalField(
        max_digits=6, decimal_places=3, default=0.000, help_text="Peso em Kg"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'loja'
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    def __str__(self):
        return self.nome

    @property
    def imagem_principal(self):
        imagens = self.imagens.all()
        return next((imagem for imagem in imagens if imagem.principal), imagens.first())

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("loja:produto_publico", kwargs={"slug": self.slug})
    
    def save(self, *args, **kwargs):
        if self.__class__ is Produto:
            raise ValueError(
                "Produto deve ser criado através de uma classe filha."
            )

        super().save(*args, **kwargs)

    # @abstractmethod
    def custo_producao_total(self) -> Decimal:
        # """Contrato: obriga todas as classes filhas a explicitar como calculam o custo de produção."""
        raise NotImplementedError

class ProdutoImagem(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    produto = models.ForeignKey(
        "loja.Produto",
        on_delete=models.CASCADE,
        related_name="imagens",
        verbose_name="Produto",
    )

    imagem = models.ImageField(
        upload_to="produtos/",
        verbose_name="Imagem",
    )

    ordem = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem",
    )

    principal = models.BooleanField(
        default=False,
        verbose_name="Imagem principal",
    )

    class Meta:
        verbose_name = "Imagem do Produto"
        verbose_name_plural = "Imagens dos Produtos"
        ordering = ("ordem",)

    def __str__(self):
        return f"{self.produto.nome} - Imagem {self.ordem}"