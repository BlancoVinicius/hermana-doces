from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from loja.forms.clientes import ClienteForm, EnderecoForm
from loja.models import (
    Cliente, Endereco, Produto, Pedido, Pagamento,
    StatusPedido, StatusPagamento,
)
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from loja.models import Endereco

@login_required
def dashboard(request):
    pedidos_nao_cancelados = Pedido.objects.exclude(status=StatusPedido.CANCELADO)
    pedidos_pendentes = Pedido.objects.filter(
        status__in=[StatusPedido.ORCAMENTO, StatusPedido.PENDENTE]
    )
    valor_total = pedidos_nao_cancelados.aggregate(total=Sum("total"))["total"] or 0

    return render(request, "loja/painel/dashboard.html", {
        "produtos_ativos": Produto.objects.filter(ativo=True).count(),
        "total_clientes": Cliente.objects.filter(ativo=True).count(),
        "pedidos_pendentes": pedidos_pendentes.count(),
        "valor_total": valor_total,
        "pedidos_recentes": Pedido.objects.select_related(
            "cliente"
        ).order_by("-criado_em")[:10],
        "pagamentos_pendentes": Pagamento.objects.filter(
            status=StatusPagamento.PENDENTE
        ).count(),
    })

@login_required
def cliente_lista(request):
    busca = request.GET.get("q", "").strip()
    status = request.GET.get("status", "ativos").strip()
    clientes = Cliente.objects.annotate(qtd_pedidos=Count("pedidos", distinct=True))

    if busca:
        clientes = clientes.filter(
            Q(nome__icontains=busca)
            | Q(email__icontains=busca)
            | Q(telefone__icontains=busca)
            | Q(documento__icontains=busca)
        )
    if status == "ativos":
        clientes = clientes.filter(ativo=True)
    elif status == "inativos":
        clientes = clientes.filter(ativo=False)

    pagina = Paginator(clientes.order_by("nome"), 15).get_page(request.GET.get("page"))
    return render(request, "loja/painel/cliente_lista.html", {
        "pagina": pagina,
        "busca": busca,
        "status": status,
    })

@login_required
def cliente_novo(request):
    form = ClienteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        cliente = form.save()
        messages.success(request, "Cliente cadastrado com sucesso.")
        return redirect("loja:cliente_detalhe", pk=cliente.pk)
    return render(request, "loja/painel/cliente_form.html", {
        "form": form, "titulo": "Novo cliente",
    })

@login_required
def cliente_editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    form = ClienteForm(request.POST or None, instance=cliente)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Cadastro do cliente atualizado.")
        return redirect("loja:cliente_detalhe", pk=cliente.pk)
    return render(request, "loja/painel/cliente_form.html", {
        "form": form, "cliente": cliente, "titulo": "Editar cliente",
    })

@login_required
def cliente_detalhe(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    pedidos = cliente.pedidos.order_by("-criado_em")
    total_pedidos = pedidos.count()
    valor_total_pedidos = pedidos.exclude(status=StatusPedido.CANCELADO).aggregate(
        total=Sum("total")
    )["total"] or 0
    return render(request, "loja/painel/cliente_detalhe.html", {
        "cliente": cliente,
        "enderecos": cliente.enderecos.all(),
        "pedidos": pedidos,
        "total_pedidos": total_pedidos,
        "valor_total_pedidos": valor_total_pedidos,
    })

@login_required
@require_POST
def cliente_alternar_status(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    cliente.ativo = not cliente.ativo
    cliente.save(update_fields=["ativo", "atualizado_em"])
    messages.success(
        request,
        "Cliente reativado." if cliente.ativo else "Cliente desativado. O histórico foi preservado.",
    )
    return redirect("loja:cliente_lista")

@login_required
def endereco_novo(request, cliente_pk):
    cliente = get_object_or_404(Cliente, pk=cliente_pk)
    form = EnderecoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        endereco = form.save(commit=False)
        endereco.cliente = cliente
        endereco.save()
        messages.success(request, "Endereço cadastrado.")
        return redirect("loja:cliente_detalhe", pk=cliente.pk)
    return render(request, "loja/painel/endereco_form.html", {
        "form": form, "cliente": cliente, "titulo": "Novo endereço",
    })

@login_required
def endereco_editar(request, pk):
    endereco = get_object_or_404(Endereco.objects.select_related("cliente"), pk=pk)
    form = EnderecoForm(request.POST or None, instance=endereco)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Endereço atualizado.")
        return redirect("loja:cliente_detalhe", pk=endereco.cliente_id)
    return render(request, "loja/painel/endereco_form.html", {
        "form": form, "cliente": endereco.cliente, "endereco": endereco,
        "titulo": "Editar endereço",
    })

@login_required
@require_POST
def endereco_excluir(request, pk):
    endereco = get_object_or_404(Endereco.objects.select_related("cliente"), pk=pk)
    cliente_pk = endereco.cliente_id
    # Endereços usados em pedidos são protegidos pelo FK PROTECT do pedido.
    try:
        endereco.delete()
    except Exception:
        messages.error(request, "Não foi possível excluir este endereço: ele pode estar vinculado a um pedido.")
    else:
        messages.success(request, "Endereço excluído.")
    return redirect("loja:cliente_detalhe", pk=cliente_pk)


@login_required
@login_required
def enderecos_cliente(request):
    cliente_id = request.GET.get("cliente_id")

    enderecos = Endereco.objects.filter(
        cliente_id=cliente_id
    ).order_by("logradouro")

    dados = [
        {
            "id": str(endereco.pk),
            "texto": str(endereco),
        }
        for endereco in enderecos
    ]

    return JsonResponse(dados, safe=False)