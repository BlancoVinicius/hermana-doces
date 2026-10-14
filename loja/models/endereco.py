from django.db import models
import uuid


class Endereco(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    cliente = models.ForeignKey(
        "loja.Cliente",
        on_delete=models.CASCADE,
        related_name="enderecos",
        verbose_name="Cliente",
    )

    cep = models.CharField(
        max_length=9,
        verbose_name="CEP",
    )

    logradouro = models.CharField(
        max_length=150,
        verbose_name="Logradouro",
    )

    numero = models.CharField(
        max_length=20,
        verbose_name="Número",
    )

    complemento = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Complemento",
    )

    bairro = models.CharField(
        max_length=100,
        verbose_name="Bairro",
    )

    cidade = models.CharField(
        max_length=100,
        verbose_name="Cidade",
    )

    estado = models.CharField(
        max_length=2,
        verbose_name="Estado",
    )

    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"

    def __str__(self):
        return f"{self.cliente.nome} — {self.logradouro}, {self.numero} - {self.bairro} ({self.cidade}/{self.estado})"