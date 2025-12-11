from django.forms import ModelForm
from mycompany.models import MyCompanyModel


# Company Form
class MyCompanyForm(ModelForm):
    class Meta:
        model = MyCompanyModel
        fields = "__all__"
