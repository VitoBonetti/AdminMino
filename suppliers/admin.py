from django.contrib import admin
from suppliers.models import SupplierModel, LoadingAddressModel
from django.forms import inlineformset_factory

LoadingAddressFormSet = inlineformset_factory(SupplierModel, LoadingAddressModel, fields='__all__',
                                              extra=1, can_delete=True, can_delete_extra=True)


class InlineSupplier(admin.TabularInline):
    model = LoadingAddressModel

    def get_formset(self, request, obj=None, **kwargs):
        if obj:
            self.formset = inlineformset_factory(SupplierModel, self.model, fields='__all__', extra=1, can_delete=True)
        return super(InlineSupplier, self).get_formset(request, obj, **kwargs)


class AdminSupplierModel(admin.ModelAdmin):
    inlines = [InlineSupplier]


admin.site.register(SupplierModel, AdminSupplierModel)
admin.site.register(LoadingAddressModel)
