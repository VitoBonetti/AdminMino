from django.urls import path
from taxes.views import fetch_quarters, taxes_view, fetch_cost_view

urlpatterns = [
    path('', taxes_view, name='taxes'),
    path('fetch_quarters/', fetch_quarters, name='fetch_quarters'),
    path('fetch_tax_data/', fetch_cost_view, name='fetch_tax_data'),
]