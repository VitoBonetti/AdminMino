from django.forms import (
    ModelForm,
    Select,
    TextInput
)
from entries.models import EntryModel, EntryProductsModel
from django.forms import inlineformset_factory
from AdminMino.utils import FlexibleDateField
from suppliers.models import SupplierModel
from customers.models import CustomerModel
from mycompany.models import MyCompanyModel


class EntryForm(ModelForm):
    date = FlexibleDateField(input_formats=['%d-%m-%Y'],
                             widget=TextInput(attrs={'placeholder': 'ddmmyy or ddmmyyyy or ddmm'}))

    class Meta:
        model = EntryModel
        fields = "__all__"
        widgets = {
            'customer_id': Select(attrs={'required': False}),
            'supplier_id': Select(attrs={'required': False}),
        }


class EntryModelForm(ModelForm):
    class Meta:
        model = EntryModel
        fields = [
            'date',
            'overdue_date',
            'company_id',
            'customer_id',
            'supplier_id',
            'loading_address',
            'is_invoice',
            'is_commission',
            'is_quotation',
            'is_paid',
            'pallets_quantity',
            'pallets_price',
            'pallets_notes',
            'no_btw_total',
            'btw_total',
            'discount',
            'btw_total_discount',
            'loading_info',
            'transport_gross',
            'transport_price_for_ton',
            'transport_diesel_toeslag',
            'transport_extra_stop',
            'transport_extra_stop_cost',
            'notes',
        ]

    def __init__(self, *args, **kwargs):
        super(EntryModelForm, self).__init__(*args, **kwargs)
        self.fields['company_id'].queryset = MyCompanyModel.objects.filter(is_active=True)
        self.fields['customer_id'].queryset = CustomerModel.objects.filter(is_active=True)
        self.fields['supplier_id'].queryset = SupplierModel.objects.filter(is_active=True)


class EntryProductsForm(ModelForm):
    class Meta:
        model = EntryProductsModel
        fields = ["name", "description", "quantity", "unity", "unity_price", "discount"]


EntryProductsFormSet = (
    inlineformset_factory(EntryModel, EntryProductsModel,
                          form=EntryProductsForm, extra=1, can_delete=True, can_delete_extra=True))
EntryProductsFormSetNoExtra = (
    inlineformset_factory(EntryModel, EntryProductsModel,
                          form=EntryProductsForm, extra=0, can_delete=True, can_delete_extra=True))