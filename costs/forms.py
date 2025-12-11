from django.forms import (
    ModelForm,
    ModelChoiceField,
    TextInput
)
from costs.models import (
    CategoryModel,
    DescriptionModel,
    CostModel
)
from AdminMino.utils import FlexibleDateField


# Category Form
class CategoryForm(ModelForm):
    class Meta:
        model = CategoryModel
        fields = "__all__"


# Description Form
class DescriptionForm(ModelForm):
    categoryID = ModelChoiceField(queryset=CategoryModel.objects.all(), label="Category",
                                  empty_label="Select a category", required=True)

    class Meta:
        model = DescriptionModel
        fields = "__all__"


# Cost Form
class CostForm(ModelForm):
    cost_date = FlexibleDateField(input_formats=["%d-%m-%Y"],
                                  widget=TextInput(attrs={"placeholder": "ddmmyy or ddmmyyyy or ddmm"}))

    class Meta:
        model = CostModel
        fields = [
            "cost_date",
            "category_id",
            "description_id",
            "euro_amount",
            "is_credit",
            "cost_note",
        ]
