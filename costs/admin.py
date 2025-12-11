from django.contrib import admin
from costs.models import (
    DescriptionModel,
    CategoryModel,
    CostModel
)

admin.site.register(DescriptionModel)
admin.site.register(CategoryModel)
admin.site.register(CostModel)