from django.urls import path
from suppliers.views import (
    SupplierView,
    NewSupplierView,
    UpdateSupplierView,
    supplier_detail_view,
    delete_supplier,
    DeleteSupplierView,
    search_supplier,
)

urlpatterns = [
    path('', SupplierView.as_view(), name="suppliers"),
    path('delete/<int:pk>/', DeleteSupplierView.as_view(), name="delete-suppliers"),
    path('new-supplier/', NewSupplierView.as_view(), name="edit-supplier"),
    path('update-supplier/<int:pk>', UpdateSupplierView.as_view(), name="update-supplier"),
    path('delete-supplier/<int:pk>', delete_supplier, name="delete-supplier"),
    path('detail-supplier/<int:pk>', supplier_detail_view, name="detail-supplier"),
    path('search-supplier/', search_supplier, name="search-supplier"),
]