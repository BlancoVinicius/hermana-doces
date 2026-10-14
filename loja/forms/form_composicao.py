from django import forms

from loja.models import DoceInsumo, Insumo, ItemKit, Produto


class DoceInsumoForm(forms.ModelForm):
    class Meta:
        model = DoceInsumo
        fields = ("insumo", "quantidade")
        widgets = {
            "insumo": forms.Select(attrs={"class": "form-select"}),
            "quantidade": forms.NumberInput(attrs={
                "class": "form-control", "step": "0.001", "min": "0.001"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["insumo"].queryset = Insumo.objects.order_by("nome")


class ItemKitForm(forms.ModelForm):
    class Meta:
        model = ItemKit
        fields = ("produto", "quantidade")
        widgets = {
            "produto": forms.Select(attrs={"class": "form-select"}),
            "quantidade": forms.NumberInput(attrs={
                "class": "form-control", "step": "1", "min": "1"
            }),
        }

    def __init__(self, *args, kit=None, **kwargs):
        super().__init__(*args, **kwargs)
        produtos = Produto.objects.filter(ativo=True).order_by("nome")
        if kit is not None and kit.pk:
            produtos = produtos.exclude(pk=kit.pk)
        self.fields["produto"].queryset = produtos

    def clean_quantidade(self):
        quantidade = self.cleaned_data["quantidade"]
        if quantidade < 1:
            raise forms.ValidationError("A quantidade deve ser pelo menos 1.")
        return quantidade
