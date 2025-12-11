from django.forms import ModelForm
from suppliers.models import SupplierModel, LoadingAddressModel
from django.forms import inlineformset_factory


class SupplierForm(ModelForm):
    class Meta:
        model = SupplierModel
        fields = "__all__"


class LoadingAddressForm(ModelForm):
    class Meta:
        model = LoadingAddressModel
        fields = "__all__"


LoadingAddressFormSet = (
    inlineformset_factory(SupplierModel, LoadingAddressModel,
                          form=LoadingAddressForm, extra=1, can_delete=True, can_delete_extra=True))
LoadingAddressFormSetNoExtra = (
    inlineformset_factory(SupplierModel, LoadingAddressModel,
                          form=LoadingAddressForm, extra=0, can_delete=True, can_delete_extra=True))