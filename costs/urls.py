from django.urls import path
from costs.views import (
    CategoryView,
    CategoryAutocompleteView,
    DeleteCategoryView,
    DescriptionView,
    DeleteDescriptionView,
    get_description,
    get_descriptions_by_category,
    CostView,
    DeleteCostView,
    fetch_descriptions,
    export_costs_excel,
)

urlpatterns = [
    path('', CostView.as_view(), name="costs"),
    path('delete/<int:pk>/', DeleteCostView.as_view(), name="delete-cost"),
    path('fetch-descriptions/<int:category_id>/', fetch_descriptions, name='fetch-description'),
    path('categories/', CategoryView.as_view(), name="categories"),
    path('category-autocomplete/', CategoryAutocompleteView.as_view(), name="category-autocomplete"),
    path('categories/delete/<int:pk>/', DeleteCategoryView.as_view(), name="delete-category"),
    path('descriptions/', DescriptionView.as_view(), name="descriptions"),
    path('descriptions/delete/<int:pk>/', DeleteDescriptionView.as_view(), name='delete-description'),
    path('descriptions/get-description/<int:description_id>/', get_description, name='get-description'),
    path('descriptions/get-by-category/<int:category_id>/', get_descriptions_by_category,
         name='get-descriptions-by-category'),
    path('export-excel/', export_costs_excel, name='export-costs-excel'),
]