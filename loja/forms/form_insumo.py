from django import forms
from loja.models import Insumo

class InsumoForm(forms.ModelForm):
    class Meta:
        model = Insumo
        fields = [
            "nome",
            "unidade_medida",
            "custo_unitario",
            "estoque_atual",
            "estoque_minimo",
        ]

        widgets = {
            "nome": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nome do insumo",
            }),
            "unidade_medida": forms.Select(attrs={
                "class": "form-select",
            }),
            "custo_unitario": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.0001",
                "min": "0",
            }),
            "estoque_atual": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.001",
                "min": "0",
            }),
            "estoque_minimo": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.001",
                "min": "0",
            }),
        }

        labels = {
            "nome": "Nome",
            "unidade_medida": "Unidade de medida",
            "custo_unitario": "Custo unitário (R$)",
            "estoque_atual": "Estoque atual",
            "estoque_minimo": "Estoque mínimo",
        }
