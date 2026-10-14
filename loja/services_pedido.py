from decimal import Decimal

from django.db import transaction
from django.core.exceptions import ValidationError

from loja.models import ItemPedido, Pedido


@transaction.atomic
def criar_pedido(*, dados_pedido, dados_itens):
    """Cria o pedido e seus itens em lote, usando preços atuais do servidor."""
    produtos_quantidades = [
        (item["produto"], item["quantidade"])
        for item in dados_itens
        if item.get("produto") and not item.get("DELETE", False)
    ]
    if not produtos_quantidades:
        raise ValidationError("O pedido precisa conter pelo menos um produto.")

    subtotal = sum(
        (produto.preco * quantidade for produto, quantidade in produtos_quantidades),
        Decimal("0.00"),
    )
    frete = dados_pedido["frete"]
    desconto = dados_pedido["desconto"]
    if desconto > subtotal + frete:
        raise ValidationError("O desconto não pode ser maior que o subtotal somado ao frete.")

    pedido = Pedido.objects.create(
        cliente=dados_pedido["cliente"],
        endereco_entrega=dados_pedido["endereco_entrega"] or None,
        status=dados_pedido["status"],
        frete=frete,
        desconto=desconto,
        subtotal=subtotal,
        total=subtotal + frete - desconto,
    )

    ItemPedido.objects.bulk_create([
        ItemPedido(
            pedido=pedido,
            produto=produto,
            quantidade=quantidade,
            preco_unitario=produto.preco,
            preco_total=produto.preco * quantidade,
        )
        for produto, quantidade in produtos_quantidades
    ])
    return pedido
