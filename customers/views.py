from django.shortcuts import (
    render,
    get_object_or_404,
    reverse,
)
from django.views import View
from customers.models import CustomerModel
from customers.forms import CustomerForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required


class CustomerView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        customer_id = request.GET.get('id', None)

        if customer_id:
            customer = get_object_or_404(CustomerModel, pk=customer_id)
            form = CustomerForm(instance=customer)
        else:
            form = CustomerForm()

        customers = CustomerModel.objects.all()

        context = {
            "form": form,
            "customers": customers,
        }

        return render(request, "customers/customers.html", context=context)

    def post(self, request, *args, **kwargs):
        customer_id = request.POST.get("id", None)
        if customer_id:
            customer = get_object_or_404(CustomerModel, pk=customer_id)
            form = CustomerForm(request.POST, instance=customer)
        else:
            form = CustomerForm(request.POST)

        if form.is_valid():
            form.save()
            form = CustomerForm()

        customers = CustomerModel.objects.all()
        context = {
            "form": form,
            "customers": customers,
        }
        return render(request, "customers/customers.html", context=context)


class DeleteCustomerView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        customer_id = self.kwargs['pk']
        customer = get_object_or_404(CustomerModel, pk=customer_id)
        customer.delete()
        return HttpResponseRedirect(reverse('customers'))


@login_required
def search_customer(request):
    query = request.GET.get('q', '')
    if query:
        customers = CustomerModel.objects.filter(
            Q(name__icontains=query) |
            Q(address__icontains=query) |
            Q(postcode__icontains=query) |
            Q(city__icontains=query) |
            Q(nation__icontains=query) |
            Q(email__icontains=query)
        ).values('id', 'name', 'address', 'postcode', 'city', 'nation', 'phone', 'email', 'btw', 'kvk',
                 'bankaccountname', 'iban', 'is_active')
    else:
        customers = CustomerModel.objects.all().values('id', 'name', 'address', 'postcode', 'city', 'nation', 'phone',
                                                       'email', 'btw', 'kvk', 'bankaccountname', 'iban', 'is_active')
    customers_list = list(customers)

    return JsonResponse({"customers": customers_list, "count": len(customers_list)})


@login_required
def get_customer_details(request, pk):
    customer_data = get_object_or_404(CustomerModel, pk=pk)
    customer = {
        "name": customer_data.name,
        "address": customer_data.address,
        "postcode": customer_data.postcode,
        "city": customer_data.city,
        "nation": customer_data.nation,
        "phone": customer_data.phone,
        "email": customer_data.email,
        "btw": customer_data.btw,
        "kvk": customer_data.kvk,
        "bankaccountname": customer_data.bankaccountname,
        "iban": customer_data.iban,
        "is_active": customer_data.is_active
    }

    if customer:
        return JsonResponse(customer)
    else:
        return JsonResponse({"error": "No customer"}, status=404)
