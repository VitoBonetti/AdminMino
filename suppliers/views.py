from django.shortcuts import (
    get_object_or_404,
    reverse,
    redirect
)
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from suppliers.models import SupplierModel, LoadingAddressModel
from suppliers.forms import SupplierForm, LoadingAddressFormSet, LoadingAddressFormSetNoExtra
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.db.models import Q


class SupplierInLineView(LoginRequiredMixin):
    form_class = SupplierForm
    model = SupplierModel
    template_name = "suppliers/edit-supplier.html"

    def form_valid(self, form):
        context = self.get_context_data()
        named_formsets = context['named_formsets']

        # for formset in named_formsets.values():
        #     print(formset.errors)

        if form.is_valid() and all((x.is_valid() for x in named_formsets.values())):
            self.object = form.save()
            for name, formset in named_formsets.items():
                formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
                if formset_save_func is not None:
                    formset_save_func(formset)
                else:
                    formset.instance = self.object
                    formset.save()
                    print(f"FORMSET_INSTANCE= {formset.instance}")
            return redirect('suppliers')
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def formset_addresses_valid(self, formset):
        loadingaddresses = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for address in loadingaddresses:
            address.supplier_id = self.object
            address.save()


class NewSupplierView(SupplierInLineView, CreateView):
    def form_valid(self, form):
        # first save the supplier instance
        self.object = form.save()

        # then create the LoadingAddressFormSet with the instance argument
        address_formset = LoadingAddressFormSet(self.request.POST, instance=self.object, prefix='addresses')
        if not address_formset.is_valid():
            # this will save the addresses with the correct supplier_id
            #     address_formset.save()
            # else:
            # handle formset validation errors
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['named_formsets'] = {
                "addresses": LoadingAddressFormSet(self.request.POST, prefix='addresses')
            }
            print(f"REQUEST-POST: {self.request.POST}")
        else:
            context['named_formsets'] = {
                "addresses": LoadingAddressFormSet(prefix='addresses')
            }
        return context


class UpdateSupplierView(SupplierInLineView, UpdateView):
    def get_context_data(self, **kwargs):
        context = super(UpdateSupplierView, self).get_context_data(**kwargs)
        context['supplier'] = self.object
        if self.request.method == 'POST':
            context['named_formsets'] = {
                "addresses": LoadingAddressFormSetNoExtra(self.request.POST, instance=self.object, prefix='addresses')
            }
        else:
            context['named_formsets'] = {
                "addresses": LoadingAddressFormSetNoExtra(instance=self.object, prefix='addresses')
            }
        return context


class SupplierView(LoginRequiredMixin, ListView):
    model = SupplierModel
    template_name = "suppliers/suppliers.html"
    context_object_name = "suppliers"


@login_required
def delete_supplier(request, pk):
    try:
        supplier = SupplierModel.objects.get(id=pk)
    except SupplierModel.DoesNotExist:
        messages.success(
            request, 'Object does not exist'
        )

    return redirect('edit-supplier', pk=supplier.supplier_id.id)


class DeleteSupplierView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        supplier_id = self.kwargs['pk']
        supplier = get_object_or_404(SupplierModel, pk=supplier_id)
        supplier.delete()
        return HttpResponseRedirect(reverse('suppliers'))


@login_required()
def supplier_detail_view(request, pk):
    supplier = get_object_or_404(SupplierModel, id=pk)
    loadingaddresses = LoadingAddressModel.objects.filter(supplier_id=supplier)

    # Manually constructing the list of dictionaries for loading addresses
    loading_addresses_data = [
        {
            "address": address.address,
            "postcode": address.postcode,
            "city": address.city,
            "nation": address.nation,
        }
        for address in loadingaddresses
    ]

    supplier_data = {
        "name": supplier.name,
        "address": supplier.address,
        "postcode": supplier.postcode,
        "city": supplier.city,
        "nation": supplier.nation,
        "phone": supplier.phone,
        "email": supplier.email,
        "kvk": supplier.kvk,
        "btw": supplier.btw,
        "bankaccountname": supplier.bankaccountname,
        "iban": supplier.iban,
        "is_active": supplier.is_active
        # If there are more fields, continue listing them here
    }

    context = {
        "supplier": supplier_data,
        "loadingaddresses": loading_addresses_data,
    }

    # return render(request, "suppliers/supplier-detail.html", context=context)
    return JsonResponse(context)


@login_required
def search_supplier(request):
    query = request.GET.get('q', '')
    if query:
        suppliers = SupplierModel.objects.filter(
            Q(name__icontains=query) |
            Q(city__icontains=query) |
            Q(nation__icontains=query)
        ).values('id', 'name', 'address', 'postcode', 'city', 'nation', 'phone', 'email', 'btw', 'kvk',
                 'bankaccountname', 'iban')
    else:
        suppliers = SupplierModel.objects.all().values('id', 'name', 'address', 'postcode', 'city', 'nation', 'phone',
                                                       'email', 'btw', 'kvk', 'bankaccountname', 'iban', 'is_active')

    suppliers_list = list(suppliers)  # Convert QuerySet to list for JSON serialization
    return JsonResponse({'suppliers': suppliers_list, 'count': len(suppliers_list)})