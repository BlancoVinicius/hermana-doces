from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("loja", "0005_cliente_endereco_pedido_pagamento_itempedido"),
    ]

    operations = [
        migrations.AddField(
            model_name="cliente",
            name="ativo",
            field=models.BooleanField(default=True, verbose_name="Ativo"),
        ),
    ]
