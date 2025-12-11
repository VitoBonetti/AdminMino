
from django.contrib import admin
from entries.models import EntryModel, EntryProductsModel
from django.forms import inlineformset_factory

EntryProductsFormSet = inlineformset_factory(EntryModel, EntryProductsModel,
                                             fields='__all__', extra=1, can_delete=True, can_delete_extra=True)


class InlineEntry(admin.TabularInline):
    model = EntryProductsModel

    def get_formset(self, request, obj=None, **kwargs):
        if obj:
            self.formset = inlineformset_factory(EntryModel, self.model, fields='__all__', extra=1, can_delete=True)
        return super(InlineEntry, self).get_formset(request, obj, **kwargs)


class AdminEntryModel(admin.ModelAdmin):
    inlines = [InlineEntry]


admin.site.register(EntryModel, AdminEntryModel)