from django import forms
from loja.models import ProdutoImagem


class ProdutoImagemForm(forms.ModelForm):
    class Meta:
        model = ProdutoImagem
        fields = ("imagem", "ordem", "principal")
        widgets = {
            "imagem": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "ordem": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "principal": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
