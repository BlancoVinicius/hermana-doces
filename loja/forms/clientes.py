from django import forms

from loja.models import Cliente, Endereco


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = (
            "nome",
            "email",
            "telefone",
            "documento",
            "aceita_receber_propaganda",
            "ativo",
        )
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telefone": forms.TextInput(attrs={"class": "form-control"}),
            "documento": forms.TextInput(attrs={"class": "form-control"}),
            "aceita_receber_propaganda": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "ativo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class EnderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        fields = (
            "cep", "logradouro", "numero", "complemento",
            "bairro", "cidade", "estado",
        )
        widgets = {
            "cep": forms.TextInput(attrs={"class": "form-control", "placeholder": "00000-000"}),
            "logradouro": forms.TextInput(attrs={"class": "form-control"}),
            "numero": forms.TextInput(attrs={"class": "form-control"}),
            "complemento": forms.TextInput(attrs={"class": "form-control"}),
            "bairro": forms.TextInput(attrs={"class": "form-control"}),
            "cidade": forms.TextInput(attrs={"class": "form-control"}),
            "estado": forms.TextInput(attrs={"class": "form-control", "maxlength": "2"}),
        }

    def clean_estado(self):
        return self.cleaned_data["estado"].strip().upper()

    def clean_cep(self):
        return self.cleaned_data["cep"].strip()
