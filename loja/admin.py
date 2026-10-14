from django.contrib import admin
from polymorphic.admin import (
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter,
    PolymorphicParentModelAdmin,
)

from .models import (
    Categoria,
    Doce,
    DoceInsumo,
    Insumo,
    Produto,
    Kit,
    ItemKit,
    Cliente,
    Endereco,
    Pedido,
    ItemPedido,
    Pagamento,
)

# ==========================================
# 1. CATEGORIA E INSUMO
# ==========================================
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "slug", "ordem", "ativa")
    list_filter = ("ativa",)
    search_fields = ("nome", "slug")
    prepopulated_fields = {"slug": ("nome",)}

@admin.register(Produto)
class ProdutoAdmin(PolymorphicParentModelAdmin):
    base_model = Produto
    child_models = (Doce, Kit)

    list_display = (
        "nome",
        "categoria",
        "ativo",
        "destaque",
        "criado_em",
    )

    list_filter = (
        PolymorphicChildModelFilter,
        "categoria",
        "ativo",
        "destaque",
    )

    search_fields = (
        "nome",
        "slug",
    )

    ordering = ("nome",)


# ==========================================
# 2. FICHA TÉCNICA (INLINE DO DOCE)
# ==========================================

class DoceInsumoInline(admin.TabularInline):
    model = DoceInsumo
    extra = 1

    autocomplete_fields = ("insumo",)

    fields = (
        "insumo",
        "quantidade",
        "custo_item_display",
    )

    readonly_fields = ("custo_item_display",)

    @admin.display(description="Custo")
    def custo_item_display(self, obj):
        if not obj.pk or not obj.insumo:
            return "R$ 0,00"

        return f"R$ {obj.custo_item:.2f}"


@admin.register(Doce)
class DoceAdmin(PolymorphicChildModelAdmin):
    base_model = Doce
    show_in_index = True

    inlines = (DoceInsumoInline,)

    list_display = (
        "nome",
        "categoria",
        "ativo",
        "destaque",
        "custo_producao_display",
    )

    list_filter = (
        "categoria",
        "ativo",
        "destaque",
    )

    search_fields = (
        "nome",
        "slug",
    )

    prepopulated_fields = {
        "slug": ("nome",),
    }

    @admin.display(description="Custo de produção")
    def custo_producao_display(self, obj):
        return f"R$ {obj.custo_producao_total:.2f}"

# # ==========================================
# # 4. KIT
# # ==========================================
class ItemKitInline(admin.TabularInline):
    model = ItemKit
    fk_name = "kit"
    extra = 1

    autocomplete_fields = ("produto",)

    fields = (
        "produto",
        "quantidade",
    )


@admin.register(Kit)
class KitAdmin(PolymorphicChildModelAdmin):
    base_model = Kit
    show_in_index = True

    inlines = (ItemKitInline,)

    list_display = (
        "nome",
        "categoria",
        "ativo",
        "destaque",
        "criado_em",
    )

    list_filter = (
        "categoria",
        "ativo",
        "destaque",
    )

    search_fields = (
        "nome",
        "slug",
    )

    prepopulated_fields = {
        "slug": ("nome",),
    }



@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):

    list_display = (
        "nome",
        "unidade_medida",
        "custo_unitario",
        "estoque_atual",
        "estoque_minimo",
        "precisa_reposicao",
    )

    list_filter = (
        "unidade_medida",
    )

    search_fields = (
        "nome",
    )

    ordering = (
        "nome",
    )

    readonly_fields = (
        "criado_em",
        "atualizado_em",
    )

    @admin.display(
        boolean=True,
        description="Precisa Reposição?"
    )
    def precisa_reposicao(self, obj):
        return obj.precisa_reposicao



class EnderecoInline(admin.TabularInline):
    model = Endereco
    extra = 1

    fields = (
        "cep",
        "logradouro",
        "numero",
        "complemento",
        "bairro",
        "cidade",
        "estado",
    )


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    inlines = (EnderecoInline,)

    list_display = (
        "nome",
        "email",
        "telefone",
        "documento",
        "aceita_receber_propaganda",
        "criado_em",
    )

    list_filter = (
        "aceita_receber_propaganda",
    )

    search_fields = (
        "nome",
        "email",
        "telefone",
        "documento",
    )

    ordering = (
        "nome",
    )

    readonly_fields = (
        "criado_em",
        "atualizado_em",
    )

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 1

    # autocomplete_fields = (
    #     "produto",
    # )

    fields = (
        "produto",
        "quantidade",
        # "preco_unitario",
        "preco_total",
    )

    readonly_fields = (
        "preco_total",
    )

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    inlines = (ItemPedidoInline,)

    list_display = (
        "id",
        "cliente",
        "status",
        "subtotal",
        "frete",
        "desconto",
        "total",
        "criado_em",
    )

    list_filter = (
        "status",
        "criado_em",
    )

    search_fields = (
        "id",
        "cliente__nome",
        "cliente__email",
    )

    ordering = (
        "-criado_em",
    )

    readonly_fields = (
        "subtotal",
        "total",
        "criado_em",
        "atualizado_em",
    )

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = (
        "pedido",
        "status",
        "metodo",
        "valor",
        "transacao_id",
        "criado_em",
    )

    list_filter = (
        "status",
        "metodo",
        "criado_em",
    )

    search_fields = (
        "pedido__id",
        "pedido__cliente__nome",
        "transacao_id",
    )

    ordering = (
        "-criado_em",
    )

    readonly_fields = (
        "criado_em",
    )

# # ==========================================
# # 3. POLIMORFISMO (PRODUTO E DOCE)
# # ==========================================
# class ProdutoChildAdmin(PolymorphicChildModelAdmin):
#     """Classe base para os filhos de Produto no Admin."""

#     base_model = Produto


# @admin.register(Doce)
# class DoceAdmin(ProdutoChildAdmin):
#     base_model = Doce
#     show_in_index = True
#     # inlines = [DoceInsumoInline]
#     list_display = (
#         "nome",
#         "categoria",
#         "ativo",
#         "destaque",
#         "custo_producao_display",
#     )
#     search_fields = ("nome", "slug")
#     prepopulated_fields = {"slug": ("nome",)}

#     @admin.display(description="Custo de Produção")
#     def custo_producao_display(self, obj):
#         return f"R$ {obj.custo_producao_total:.2f}"



# # class ItemKitInline(admin.TabularInline):
# #     model = ItemKit
# #     extra = 1
# #     autocomplete_fields = ["produto"]


# @admin.register(ItemKit)
# class ItemKitAdmin(admin.ModelAdmin):
#     list_display = [
#         "kit",
#         "produto",
#         "quantidade",
#     ]

#     list_filter = [
#         "kit",
#     ]

#     search_fields = [
#         "kit__nome",
#         "produto__nome",
#     ]

#     autocomplete_fields = [
#         "kit",
#         "produto",
#     ]


# class ItemKitInline(admin.TabularInline):
#     model = ItemKit
#     fk_name = "kit"
#     extra = 1
#     autocomplete_fields = ["produto"]


# @admin.register(Kit)
# class KitAdmin(ProdutoChildAdmin):
#     base_model = Kit
#     show_in_index = True

#     inlines = [ItemKitInline]

#     list_display = (
#         "nome",
#         "categoria",
#         "ativo",
#         "destaque",
#         "criado_em",
#     )

#     search_fields = ("nome", "slug")

#     prepopulated_fields = {
#         "slug": ("nome",)
#     }


