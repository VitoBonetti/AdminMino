from django.urls import path
from customers.views import (
    CustomerView,
    DeleteCustomerView,
    search_customer,
    get_customer_details,
)

urlpatterns = [
    path('', CustomerView.as_view(), name="customers"),
    path('delete/<int:pk>/', DeleteCustomerView.as_view(), name="delete-customer"),
    path('details/<int:pk>/', get_customer_details, name="customer-details"),
    path('search-customer/', search_customer, name="search-customer"),
]