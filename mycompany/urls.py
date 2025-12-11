from django.urls import path
from mycompany.views import (
    CompanyView,
    DeleteCompanyView,
    get_mycompany_details
)

urlpatterns = [
    path('', CompanyView.as_view(), name="mycompany"),
    path('delete/<int:pk>/', DeleteCompanyView.as_view(), name="delete-mycompany"),
    path('details/', get_mycompany_details, name="company-details"),
]