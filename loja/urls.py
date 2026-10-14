from django.urls import path
from django.contrib.auth import views as auth_views

from loja import views_clientes
from loja.views import (
    insumo_lista, insumo_criar, insumo_editar, insumo_confirmar_exclusao, insumo_excluir,
    produto_excluir, doce_insumo_adicionar, doce_insumo_remover, item_kit_adicionar,
    item_kit_remover, imagem_adicionar, imagem_definir_principal, imagem_excluir,
    produto_lista, produto_novo, produto_editar, produto_toggle, pedido_lista,
    pedido_novo, pedido_detalhe, pedido_status, item_adicionar, item_excluir,
    pagamento_lista, pagamento_novo, pagamento_editar,
)
from loja.views_clientes import (
    dashboard, cliente_lista, cliente_novo, cliente_editar, cliente_detalhe,
    cliente_alternar_status, endereco_novo, endereco_editar, endereco_excluir,
)
from loja.views_publica import home_publica, produto_publico

app_name = "loja"

urlpatterns = [

    # Loja pública
    path("", home_publica, name="home"),
    path("catalogo/<slug:slug>/", produto_publico, name="produto_publico"),

    # Painel administrativo
    path("dashboard/", dashboard, name="dashboard"),
    path("logout/", auth_views.LogoutView.as_view(next_page="loja:home"), name="logout"),

    # Produtos
    path("produtos/", produto_lista, name="produto_lista"),
    path("produtos/novo/", produto_novo, name="produto_novo"),
    path("produtos/<uuid:pk>/editar/", produto_editar, name="produto_editar"),
    path("produtos/<uuid:pk>/alternar-status/", produto_toggle, name="produto_toggle"),
    path("produtos/<uuid:pk>/excluir/", produto_excluir, name="produto_excluir"),
    path("produtos/<uuid:pk>/insumos/adicionar/", doce_insumo_adicionar, name="doce_insumo_adicionar"),
    path("doce-insumos/<uuid:pk>/remover/", doce_insumo_remover, name="doce_insumo_remover"),
    path("produtos/<uuid:pk>/itens-kit/adicionar/", item_kit_adicionar, name="item_kit_adicionar"),
    path("itens-kit/<int:pk>/remover/", item_kit_remover, name="item_kit_remover"),
    path("produtos/<uuid:pk>/imagens/adicionar/", imagem_adicionar, name="imagem_adicionar"),
    path("imagens/<uuid:pk>/principal/", imagem_definir_principal, name="imagem_principal"),
    path("imagens/<uuid:pk>/excluir/", imagem_excluir, name="imagem_excluir"),

    # Insumos
    path("insumos/", insumo_lista, name="insumo_lista"),
    path("insumos/novo/", insumo_criar, name="insumo_criar"),
    path("insumos/<uuid:pk>/editar/", insumo_editar, name="insumo_editar"),
    path("insumos/<uuid:pk>/excluir/", insumo_confirmar_exclusao, name="insumo_confirmar_exclusao"),
    path("insumos/<uuid:pk>/excluir/confirmado/", insumo_excluir, name="insumo_excluir"),

    # Categorias: o CRUD de categorias ainda deve ser ligado às views próprias.
    path("categoria_lista/", insumo_lista, name="categoria_lista"),

    # Clientes: não há exclusão física; somente desativação reversível.
    path("clientes/", cliente_lista, name="cliente_lista"),
    path("clientes/novo/", cliente_novo, name="cliente_novo"),
    path("clientes/<uuid:pk>/", cliente_detalhe, name="cliente_detalhe"),
    path("clientes/<uuid:pk>/editar/", cliente_editar, name="cliente_editar"),
    path("clientes/<uuid:pk>/alternar-status/", cliente_alternar_status, name="cliente_alternar_status"),
    path("clientes/<uuid:cliente_pk>/enderecos/novo/", endereco_novo, name="endereco_novo"),
    path("enderecos/<uuid:pk>/editar/", endereco_editar, name="endereco_editar"),
    path("enderecos/<uuid:pk>/excluir/", endereco_excluir, name="endereco_excluir"),

    # Pedidos e itens
    path("pedidos/", pedido_lista, name="pedido_lista"),
    path("pedidos/novo/", pedido_novo, name="pedido_novo"),
    path("pedidos/<uuid:pk>/", pedido_detalhe, name="pedido_detalhe"),
    path("pedidos/<uuid:pk>/status/", pedido_status, name="pedido_status"),
    path("pedidos/<uuid:pk>/itens/adicionar/", item_adicionar, name="item_adicionar"),
    path("itens-pedido/<uuid:pk>/remover/", item_excluir, name="item_excluir"),

    # Pagamentos
    path("pagamentos/", pagamento_lista, name="pagamento_lista"),
    path("pedidos/<uuid:pedido_pk>/pagamento/", pagamento_novo, name="pagamento_novo"),
    path("pagamentos/<uuid:pk>/editar/", pagamento_editar, name="pagamento_editar"),

    # Endereços Cliente
    path("enderecos-cliente/", views_clientes.enderecos_cliente, name="enderecos_cliente"),
]
