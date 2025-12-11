from django.urls import path
from support.views import DeleteTicketView, support_view

urlpatterns = [
    path('', support_view, name="support"),
    path('delete/<int:pk>/', DeleteTicketView.as_view(), name="delete-ticket"),
]