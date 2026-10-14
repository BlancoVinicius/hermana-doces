
from django import forms
from loja.models import Categoria, Doce


# class ProdutoForm(forms.ModelForm):
#     TIPO_CHOICES = [
#         ("doce", "Doce"),
#         ("kit", "Kit"),
#     ]

#     tipo = forms.ChoiceField(
#         choices=TIPO_CHOICES,
#         label="Tipo de produto",
#         widget=forms.Select(attrs={"class": "form-select"}),
#     )

#     class Meta:
#         model = Doce
#         fields = [
#             "categoria",
#             "nome",
#             "slug",
#             "descricao_curta",
#             "descricao",
#             "preco",
#             "peso_kg",
#             "destaque",
#             "ativo",
#         ]

#         widgets = {
#             "categoria": forms.Select(attrs={"class": "form-select"}),
#             "nome": forms.TextInput(attrs={"class": "form-control"}),
#             "slug": forms.TextInput(attrs={"class": "form-control"}),
#             "descricao_curta": forms.TextInput(attrs={"class": "form-control"}),
#             "descricao": forms.Textarea(attrs={
#                 "class": "form-control",
#                 "rows": 4,
#             }),
#             "preco": forms.NumberInput(attrs={
#                 "class": "form-control",
#                 "step": "0.01",
#                 "min": "0",
#             }),
#             "peso_kg": forms.NumberInput(attrs={
#                 "class": "form-control",
#                 "step": "0.001",
#                 "min": "0",
#             }),
#             "destaque": forms.CheckboxInput(attrs={
#                 "class": "form-check-input",
#             }),
#             "ativo": forms.CheckboxInput(attrs={
#                 "class": "form-check-input",
#             }),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields["categoria"].queryset = Categoria.objects.filter(
#             ativa=True
#         ).order_by("ordem", "nome")

#         if self.instance and self.instance.pk:
#             self.fields["tipo"].initial = (
#                 "kit" if self.instance.__class__.__name__ == "Kit"
#                 else "doce"
#             )


from django import forms
from django.utils.text import slugify

from loja.models import Categoria, Produto


class ProdutoForm(forms.Form):
    TIPOS = [
        ("doce", "Doce"),
        ("kit", "Kit"),
    ]

    tipo = forms.ChoiceField(
        label="Tipo de produto",
        choices=TIPOS,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    categoria = forms.ModelChoiceField(
        label="Categoria",
        queryset=Categoria.objects.none(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    nome = forms.CharField(
        label="Nome",
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    slug = forms.SlugField(
        label="Slug",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    descricao_curta = forms.CharField(
        label="Descrição curta",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    descricao = forms.CharField(
        label="Descrição",
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 4,
        }),
    )

    preco = forms.DecimalField(
        label="Preço de venda (R$)",
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "step": "0.01",
            "min": "0",
        }),
    )

    peso_kg = forms.DecimalField(
        label="Peso (kg)",
        min_value=0,
        max_digits=6,
        decimal_places=3,
        initial=0,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "step": "0.001",
            "min": "0",
        }),
    )

    destaque = forms.BooleanField(
        label="Produto em destaque",
        required=False,
        widget=forms.CheckboxInput(attrs={
            "class": "form-check-input",
        }),
    )

    ativo = forms.BooleanField(
        label="Produto ativo",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            "class": "form-check-input",
        }),
    )

    def __init__(self, *args, instance=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.instance = instance

        self.fields["categoria"].queryset = (
            Categoria.objects.filter(ativa=True).order_by("ordem", "nome")
        )

        if instance:
            self.initial.update({
                "tipo": "kit" if instance.__class__.__name__ == "Kit" else "doce",
                "categoria": instance.categoria_id,
                "nome": instance.nome,
                "slug": instance.slug,
                "descricao_curta": instance.descricao_curta,
                "descricao": instance.descricao,
                "preco": instance.preco,
                "peso_kg": instance.peso_kg,
                "destaque": instance.destaque,
                "ativo": instance.ativo,
            })

    def clean_slug(self):
        slug = self.cleaned_data.get("slug") or slugify(
            self.cleaned_data["nome"]
        )

        produtos = Produto.objects.filter(slug=slug)

        if self.instance and self.instance.pk:
            produtos = produtos.exclude(pk=self.instance.pk)

        if produtos.exists():
            raise forms.ValidationError(
                "Já existe um produto cadastrado com este slug."
            )

        return slug
