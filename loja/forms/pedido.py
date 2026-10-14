from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseFormSet, formset_factory

from loja.models import (
    Cliente,
    Endereco,
    ItemPedido,
    MetodoPagamento,
    Pagamento,
    Produto,
    StatusPagamento,
    StatusPedido,
)


class PedidoForm(forms.Form):
    cliente = forms.ModelChoiceField(
        label="Cliente",
        queryset=Cliente.objects.all(),
        widget=forms.Select(attrs={"class": "form-select", "id": "id_cliente"}),
    )
    endereco_entrega = forms.ModelChoiceField(
        label="Endereço de entrega",
        queryset=Endereco.objects.select_related("cliente").all(),
        widget=forms.Select(attrs={"class": "form-select", "id": "id_endereco_entrega"}),
    )
    status = forms.ChoiceField(
        label="Status",
        choices=StatusPedido.choices,
        initial=StatusPedido.ORCAMENTO,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    frete = forms.DecimalField(
        label="Frete (R$)", min_value=Decimal("0.00"), max_digits=10,
        decimal_places=2, initial=Decimal("0.00"),
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "0.01"}),
    )
    desconto = forms.DecimalField(
        label="Desconto (R$)", min_value=Decimal("0.00"), max_digits=10,
        decimal_places=2, initial=Decimal("0.00"),
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "0.01"}),
    )

    def clean(self):
        cleaned = super().clean()
        cliente = cleaned.get("cliente")
        endereco = cleaned.get("endereco_entrega")
        if cliente and endereco and endereco.cliente_id != cliente.pk:
            self.add_error("endereco_entrega", "Selecione um endereço pertencente ao cliente escolhido.")
        return cleaned


class ItemPedidoForm(forms.Form):
    produto = forms.ModelChoiceField(
        label="Produto",
        queryset=Produto.objects.filter(ativo=True).order_by("nome"),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    quantidade = forms.IntegerField(
        label="Quantidade", min_value=1, initial=1,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "1", "step": "1"}),
    )


class BaseItemPedidoFormSet(BaseFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        itens = [
            form.cleaned_data for form in self.forms
            if form.cleaned_data and not form.cleaned_data.get("DELETE", False)
            and form.cleaned_data.get("produto")
        ]
        if not itens:
            raise ValidationError("Adicione pelo menos um produto ao pedido.")


ItemPedidoFormSet = formset_factory(
    ItemPedidoForm, formset=BaseItemPedidoFormSet, extra=1, can_delete=True
)


class PagamentoForm(forms.ModelForm):
    valor = forms.DecimalField(
        label="Valor (R$)", min_value=Decimal("0.01"), max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "0.01", "step": "0.01"}),
    )

    class Meta:
        model = Pagamento
        fields = ("status", "metodo", "valor", "transacao_id")
        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
            "metodo": forms.Select(attrs={"class": "form-select"}),
            "valor": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "0.01"}),
            "transacao_id": forms.TextInput(attrs={"class": "form-control"}),
        }
        labels = {
            "status": "Status do pagamento",
            "metodo": "Método de pagamento",
            "valor": "Valor (R$)",
            "transacao_id": "Identificador da transação",
        }

    def __init__(self, *args, pedido=None, **kwargs):
        self.pedido = pedido
        super().__init__(*args, **kwargs)
        if pedido and self.instance._state.adding:
            self.fields["valor"].initial = pedido.total

    def clean_valor(self):
        valor = self.cleaned_data["valor"]
        if valor < Decimal("0.00"):
            raise forms.ValidationError("O valor não pode ser negativo.")
        return valor
