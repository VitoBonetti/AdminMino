
from django.urls import path
from entries.views import (
    NewEntryView,
    UpdateEntryView,
    EntryView,
    DeleteEntryView,
    delete_entry,
    EntryDetailView,
    get_loading_addresses,
    CommissionEntryView,
    QuotationEntryView,
    InvoiceEntryView,
    entry_detail_pdf
)

urlpatterns = [
    path('', EntryView.as_view(), name="entries"),
    path('delete/<int:pk>/', DeleteEntryView.as_view(), name="delete-entries"),
    path('new-entry/', NewEntryView.as_view(), name="edit-entry"),
    path('update-entry/<int:pk>', UpdateEntryView.as_view(), name="update-entry"),
    path('delete-entry/<int:pk>', delete_entry, name="delete-entry"),
    path('entry-detail/<int:pk>', EntryDetailView, name="entry-detail"),
    path('entry-detail/<int:pk>/pdf/', entry_detail_pdf, name="entry-detail-pdf"),
    path('commissions/', CommissionEntryView.as_view(), name="commissions"),
    path('quotations/', QuotationEntryView.as_view(), name="quotations"),
    path('invoices/', InvoiceEntryView.as_view(), name="invoices"),
    path('api/get-loading-addresses/', get_loading_addresses, name='get-loading-addresses'),
]