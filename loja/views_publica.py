from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404, render

from loja.models import Categoria, Produto, ProdutoImagem

def _produtos_publicos():
    return (
        Produto.objects.filter(ativo=True, categoria__ativa=True)
        .select_related("categoria")
        .prefetch_related(
            Prefetch(
                "imagens",
                queryset=ProdutoImagem.objects.order_by("-principal", "ordem"),
            )
        )
    )


def home_publica(request):
    busca = request.GET.get("q", "").strip()
    categoria_slug = request.GET.get("categoria", "").strip()

    produtos = _produtos_publicos()

    if busca:
        produtos = produtos.filter(
            Q(nome__icontains=busca)
            | Q(descricao__icontains=busca)
            | Q(descricao_curta__icontains=busca)
        )

    if categoria_slug:
        produtos = produtos.filter(categoria__slug=categoria_slug)

    produtos = produtos.order_by("categoria__ordem", "nome")

    destaques = produtos.filter(destaque=True)[:6]

    return render(
        request,
        "loja/publico/home.html",
        {
            "produtos": produtos,
            "destaques": destaques,
            "categorias": Categoria.objects.filter(ativa=True).order_by("ordem", "nome"),
            "busca": busca,
            "categoria_slug": categoria_slug,
        },
    )


def produto_publico(request, slug):
    produto = get_object_or_404(
        _produtos_publicos(),
        slug=slug,
    )
    return render(
        request,
        "loja/publico/produto.html",
        {"produto": produto},
    )