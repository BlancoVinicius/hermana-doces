from django.contrib import messages
from django.db.models import Q, ProtectedError
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db import transaction
from django.core.exceptions import ValidationError

from loja.forms import (
    InsumoForm, ProdutoForm, DoceInsumoForm, ItemKitForm, ProdutoImagemForm,
    PedidoForm, ItemPedidoForm, ItemPedidoFormSet, PagamentoForm,
)
from loja.models import (
    Insumo, Categoria, Doce, Kit, Produto, DoceInsumo, ItemKit, ProdutoImagem,
    Cliente, Endereco, Pedido, ItemPedido, Pagamento, StatusPedido, StatusPagamento,
)
from loja.services_pedido import criar_pedido


def produto_lista(request):
    busca = request.GET.get("q", "").strip()
    categoria_sel = request.GET.get("categoria", "").strip()
    status = request.GET.get("status", "").strip()

    produtos = Produto.objects.select_related("categoria").prefetch_related(
        "imagens"
    )

    if busca:
        produtos = produtos.filter(
            Q(nome__icontains=busca)
            | Q(slug__icontains=busca)
            | Q(descricao__icontains=busca)
        )

    if categoria_sel:
        produtos = produtos.filter(categoria_id=categoria_sel)

    if status == "ativos":
        produtos = produtos.filter(ativo=True)
    elif status == "inativos":
        produtos = produtos.filter(ativo=False)

    produtos = produtos.order_by("nome")

    pagina = Paginator(produtos, 10).get_page(request.GET.get("page"))

    return render(request, "loja/painel/produto_lista.html", {
        "pagina": pagina,
        "categorias": Categoria.objects.order_by("ordem", "nome"),
        "busca": busca,
        "categoria_sel": categoria_sel,
        "status": status,
    })


def produto_novo(request):
    form = ProdutoForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        dados = form.cleaned_data
        tipo = dados["tipo"]

        modelo = Doce if tipo == "doce" else Kit
        produto = modelo()

        for campo in (
            "categoria",
            "nome",
            "slug",
            "descricao_curta",
            "descricao",
            "preco",
            "peso_kg",
            "destaque",
            "ativo",
        ):
            setattr(produto, campo, dados[campo])

        produto.save()

        messages.success(request, "Produto cadastrado com sucesso.")
        return redirect("loja:produto_lista")

    return render(request, "loja/painel/produto_editar.html", {
        "form": form,
        "novo": True,
        "titulo": "Novo produto",
    })


def produto_editar(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    form = ProdutoForm(
        request.POST or None,
        instance=produto,
    )

    # A edição não deve converter um Doce em Kit, ou vice-versa.
    form.fields["tipo"].disabled = True

    if request.method == "POST" and form.is_valid():
        dados = form.cleaned_data

        for campo in (
            "categoria",
            "nome",
            "slug",
            "descricao_curta",
            "descricao",
            "preco",
            "peso_kg",
            "destaque",
            "ativo",
        ):
            setattr(produto, campo, dados[campo])

        produto.save()

        messages.success(request, "Produto atualizado com sucesso.")
        return redirect("loja:produto_editar", pk=produto.pk)

    contexto = {
        "form": form,
        "produto": produto,
        "novo": False,
        "titulo": "Editar produto",
        "imagens": produto.imagens.all(),
        "form_imagem": ProdutoImagemForm(),
        "eh_doce": isinstance(produto, Doce),
        "eh_kit": isinstance(produto, Kit),
    }

    if isinstance(produto, Doce):
        contexto.update({
            "form_doce_insumo": DoceInsumoForm(),
            "ingredientes": produto.ingredientes.select_related("insumo").all(),
        })
    elif isinstance(produto, Kit):
        contexto.update({
            "form_item_kit": ItemKitForm(kit=produto),
            "itens_kit": produto.itens.select_related("produto").all(),
        })

    return render(request, "loja/painel/produto_editar.html", contexto)


@require_POST
def doce_insumo_adicionar(request, pk):
    doce = get_object_or_404(Doce, pk=pk)
    form = DoceInsumoForm(request.POST)

    if form.is_valid():
        insumo = form.cleaned_data["insumo"]
        quantidade = form.cleaned_data["quantidade"]
        DoceInsumo.objects.update_or_create(
            doce=doce,
            insumo=insumo,
            defaults={"quantidade": quantidade},
        )
        messages.success(request, f"Insumo '{insumo.nome}' adicionado/atualizado na ficha técnica.")
    else:
        messages.error(request, f"Não foi possível adicionar o insumo: {form.errors.as_text()}")

    return redirect("loja:produto_editar", pk=doce.pk)


@require_POST
def doce_insumo_remover(request, pk):
    ingrediente = get_object_or_404(DoceInsumo, pk=pk)
    doce_pk = ingrediente.doce_id
    ingrediente.delete()
    messages.success(request, "Insumo removido da ficha técnica.")
    return redirect("loja:produto_editar", pk=doce_pk)


@require_POST
def item_kit_adicionar(request, pk):
    kit = get_object_or_404(Kit, pk=pk)
    form = ItemKitForm(request.POST, kit=kit)

    if form.is_valid():
        produto = form.cleaned_data["produto"]
        quantidade = form.cleaned_data["quantidade"]
        if produto.pk == kit.pk:
            messages.error(request, "Um kit não pode conter a si próprio.")
        else:
            ItemKit.objects.update_or_create(
                kit=kit,
                produto=produto,
                defaults={"quantidade": quantidade},
            )
            messages.success(request, f"Produto '{produto.nome}' adicionado/atualizado no kit.")
    else:
        messages.error(request, f"Não foi possível adicionar o produto: {form.errors.as_text()}")

    return redirect("loja:produto_editar", pk=kit.pk)


@require_POST
def item_kit_remover(request, pk):
    item = get_object_or_404(ItemKit, pk=pk)
    kit_pk = item.kit_id
    item.delete()
    messages.success(request, "Produto removido do kit.")
    return redirect("loja:produto_editar", pk=kit_pk)


@require_POST
def imagem_adicionar(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    form = ProdutoImagemForm(request.POST, request.FILES)

    if form.is_valid():
        imagem = form.save(commit=False)
        imagem.produto = produto
        if imagem.principal:
            produto.imagens.update(principal=False)
        elif not produto.imagens.exists():
            imagem.principal = True
        imagem.save()
        messages.success(request, "Imagem adicionada com sucesso.")
    else:
        messages.error(request, f"Não foi possível adicionar a imagem: {form.errors.as_text()}")

    return redirect("loja:produto_editar", pk=produto.pk)


@require_POST
def imagem_definir_principal(request, pk):
    imagem = get_object_or_404(ProdutoImagem, pk=pk)
    produto_pk = imagem.produto_id
    ProdutoImagem.objects.filter(produto_id=produto_pk).update(principal=False)
    imagem.principal = True
    imagem.save(update_fields=["principal"])
    messages.success(request, "Imagem principal atualizada.")
    return redirect("loja:produto_editar", pk=produto_pk)


@require_POST
def imagem_excluir(request, pk):
    imagem = get_object_or_404(ProdutoImagem, pk=pk)
    produto = imagem.produto
    era_principal = imagem.principal
    imagem.delete()

    if era_principal:
        proxima = produto.imagens.order_by("ordem").first()
        if proxima:
            proxima.principal = True
            proxima.save(update_fields=["principal"])

    messages.success(request, "Imagem excluída.")
    return redirect("loja:produto_editar", pk=produto.pk)


@require_POST
def produto_toggle(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    produto.ativo = not produto.ativo
    produto.save(update_fields=["ativo", "atualizado_em"])

    messages.success(
        request,
        "Produto ativado." if produto.ativo else "Produto desativado.",
    )
    return redirect("loja:produto_lista")


def produto_excluir(request, pk):
    produto = get_object_or_404(Produto, pk=pk)

    if request.method == "POST":
        try:
            produto.delete()
        except ProtectedError:
            messages.error(
                request,
                "Não é possível excluir este produto porque ele está "
                "vinculado a outros registros.",
            )
        else:
            messages.success(request, "Produto excluído com sucesso.")

        return redirect("loja:produto_lista")

    return render(request, "loja/painel/produto_confirmar_exclusao.html", {
        "produto": produto,
    })




# CRUD de insumos
def insumo_lista(request):
    busca = request.GET.get("q", "").strip()

    insumos = Insumo.objects.all().order_by("nome")

    if busca:
        insumos = insumos.filter(nome__icontains=busca)

    return render(
        request,
        "loja/painel/insumo/lista.html",
        {
            "insumos": insumos,
            "busca": busca,
        },
    )


def insumo_criar(request):
    form = InsumoForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()

        messages.success(
            request,
            "Insumo cadastrado com sucesso.",
        )

        return redirect("loja:insumo_lista")

    return render(
        request,
        "loja/painel/insumo/form.html",
        {
            "form": form,
            "titulo": "Cadastrar insumo",
        },
    )


def insumo_editar(request, pk):
    insumo = get_object_or_404(Insumo, pk=pk)

    form = InsumoForm(
        request.POST or None,
        instance=insumo,
    )

    if request.method == "POST" and form.is_valid():
        form.save()

        messages.success(
            request,
            "Insumo atualizado com sucesso.",
        )

        return redirect("loja:insumo_lista")

    return render(
        request,
        "loja/painel/insumo/form.html",
        {
            "form": form,
            "titulo": "Editar insumo",
            "insumo": insumo,
        },
    )


def insumo_confirmar_exclusao(request, pk):
    insumo = get_object_or_404(Insumo, pk=pk)

    return render(
        request,
        "loja/painel/insumo/confirmar_exclusao.html",
        {"insumo": insumo},
    )


@require_POST
def insumo_excluir(request, pk):
    insumo = get_object_or_404(Insumo, pk=pk)

    try:
        insumo.delete()

    except ProtectedError:
        messages.error(
            request,
            "Não é possível excluir este insumo, "
            "pois ele está vinculado a outros registros.",
        )

    else:
        messages.success(
            request,
            "Insumo excluído com sucesso.",
        )

    return redirect("loja:insumo_lista")

# ---------------------------------------------------------------------------
# PEDIDOS, ITENS DO PEDIDO E PAGAMENTOS
# ---------------------------------------------------------------------------
def pedido_lista(request):
    busca = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    pedidos = Pedido.objects.select_related("cliente", "endereco_entrega").all()
    if busca:
        filtro = Q(cliente__nome__icontains=busca) | Q(cliente__email__icontains=busca)
        try:
            from uuid import UUID
            filtro |= Q(id=UUID(busca))
        except (ValueError, TypeError, AttributeError):
            pass
        pedidos = pedidos.filter(filtro)
    if status:
        pedidos = pedidos.filter(status=status)
    pagina = Paginator(pedidos.order_by("-criado_em"), 15).get_page(request.GET.get("page"))
    return render(request, "loja/painel/pedido_lista.html", {
        "pagina": pagina,
        "busca": busca,
        "status": status,
        "status_opcoes": StatusPedido.choices,
    })


def pedido_novo(request):
    form = PedidoForm(request.POST or None)
    formset = ItemPedidoFormSet(request.POST or None, prefix="itens")
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        try:
            pedido = criar_pedido(
                dados_pedido=form.cleaned_data,
                dados_itens=[f.cleaned_data for f in formset.forms if f.cleaned_data],
            )
        except ValidationError as exc:
            form.add_error("desconto", exc.messages[0])
        else:
            messages.success(request, "Pedido cadastrado com sucesso.")
            return redirect("loja:pedido_detalhe", pk=pedido.pk)
    return render(request, "loja/painel/pedido_form.html", {
        "form": form,
        "formset": formset,
        "titulo": "Novo pedido",
    })


def pedido_detalhe(request, pk):
    pedido = get_object_or_404(
        Pedido.objects.select_related("cliente", "endereco_entrega").prefetch_related("itens__produto"),
        pk=pk,
    )
    try:
        pagamento = pedido.pagamento
    except Pagamento.DoesNotExist:
        pagamento = None
    form_item = ItemPedidoForm()
    return render(request, "loja/painel/pedido_detalhe.html", {
        "pedido": pedido,
        "itens": pedido.itens.select_related("produto").all(),
        "status_opcoes": StatusPedido.choices,
        "form_item": form_item,
        "pagamento": pagamento,
    })


@require_POST
def pedido_status(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    status = request.POST.get("status")
    if status not in StatusPedido.values:
        messages.error(request, "Status de pedido inválido.")
    else:
        pedido.status = status
        pedido.save(update_fields=["status", "atualizado_em"])
        messages.success(request, "Status do pedido atualizado.")
    return redirect("loja:pedido_detalhe", pk=pedido.pk)


@require_POST
def item_adicionar(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    form = ItemPedidoForm(request.POST)
    if form.is_valid():
        produto = form.cleaned_data["produto"]
        quantidade = form.cleaned_data["quantidade"]
        # Se o produto já estiver no pedido, aumenta a quantidade existente.
        item = pedido.itens.filter(produto=produto).first()
        if item:
            item.quantidade += quantidade
            item.save(update_fields=["quantidade", "preco_total"])
        else:
            ItemPedido.objects.create(pedido=pedido, produto=produto, quantidade=quantidade)
        messages.success(request, "Item adicionado ao pedido.")
    else:
        messages.error(request, "Não foi possível adicionar o item. Confira o produto e a quantidade.")
    return redirect("loja:pedido_detalhe", pk=pedido.pk)


@require_POST
def item_excluir(request, pk):
    item = get_object_or_404(ItemPedido.objects.select_related("pedido"), pk=pk)
    pedido = item.pedido
    item.delete()
    pedido.atualizar_totais()
    messages.success(request, "Item removido do pedido.")
    return redirect("loja:pedido_detalhe", pk=pedido.pk)


def pagamento_lista(request):
    status = request.GET.get("status", "").strip()
    pagamentos = Pagamento.objects.select_related("pedido", "pedido__cliente")
    if status:
        pagamentos = pagamentos.filter(status=status)
    pagina = Paginator(pagamentos.order_by("-criado_em"), 15).get_page(request.GET.get("page"))
    return render(request, "loja/painel/pagamento_lista.html", {
        "pagina": pagina,
        "status": status,
        "status_opcoes": StatusPagamento.choices,
    })


def pagamento_novo(request, pedido_pk):
    pedido = get_object_or_404(Pedido, pk=pedido_pk)
    try:
        pagamento = pedido.pagamento
    except Pagamento.DoesNotExist:
        pagamento = None
    if pagamento:
        return redirect("loja:pagamento_editar", pk=pagamento.pk)
    form = PagamentoForm(request.POST or None, pedido=pedido)
    if request.method == "POST" and form.is_valid():
        pagamento = form.save(commit=False)
        pagamento.pedido = pedido
        pagamento.save()
        _sincronizar_status_pedido(pedido, pagamento)
        messages.success(request, "Pagamento registrado com sucesso.")
        return redirect("loja:pedido_detalhe", pk=pedido.pk)
    return render(request, "loja/painel/pagamento_form.html", {
        "form": form, "pedido": pedido, "titulo": "Registrar pagamento",
    })


def pagamento_editar(request, pk):
    pagamento = get_object_or_404(Pagamento.objects.select_related("pedido"), pk=pk)
    form = PagamentoForm(request.POST or None, instance=pagamento, pedido=pagamento.pedido)
    if request.method == "POST" and form.is_valid():
        pagamento = form.save()
        pedido = pagamento.pedido
        _sincronizar_status_pedido(pedido, pagamento)
        messages.success(request, "Pagamento atualizado com sucesso.")
        return redirect("loja:pedido_detalhe", pk=pedido.pk)
    return render(request, "loja/painel/pagamento_form.html", {
        "form": form, "pedido": pagamento.pedido, "pagamento": pagamento,
        "titulo": "Editar pagamento",
    })


def _sincronizar_status_pedido(pedido, pagamento):
    if pagamento.status == StatusPagamento.APROVADO and pagamento.valor >= pedido.total:
        novo_status = StatusPedido.PAGO
    elif pedido.status == StatusPedido.PAGO:
        novo_status = StatusPedido.PENDENTE
    else:
        return
    if pedido.status != novo_status:
        pedido.status = novo_status
        pedido.save(update_fields=["status", "atualizado_em"])
