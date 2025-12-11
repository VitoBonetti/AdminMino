from django.forms import ModelForm
from customers.models import CustomerModel


class CustomerForm(ModelForm):
    class Meta:
        model = CustomerModel
        fields = "__all__"