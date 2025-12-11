from django.shortcuts import (
    render,
    get_object_or_404,
    reverse
)
from mycompany.models import MyCompanyModel
from mycompany.forms import MyCompanyForm
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.http import JsonResponse


# Company Views
class CompanyView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        company_id = request.GET.get("id", None)
        if company_id:
            company = get_object_or_404(MyCompanyModel, pk=company_id)
            form = MyCompanyForm(instance=company)
        else:
            form = MyCompanyForm()

        companies = MyCompanyModel.objects.all()
        context = {
            "form": form,
            "companies": companies
        }

        return render(request, "mycompany/mycompany.html", context)

    def post(self, request, *args, **kwargs):
        company_id = request.POST.get("id", None)
        if company_id:
            company = get_object_or_404(MyCompanyModel, pk=company_id)
            form = MyCompanyForm(request.POST, instance=company)
        else:
            form = MyCompanyForm(request.POST)

        if form.is_valid():
            form.save()

            form = MyCompanyForm()

        companies = MyCompanyModel.objects.all()
        context = {
            "form": form,
            "companies": companies,
        }

        return render(request, "mycompany/mycompany.html", context=context)


class DeleteCompanyView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        company_id = self.kwargs["pk"]
        company = get_object_or_404(MyCompanyModel, pk=company_id)
        company.delete()
        return HttpResponseRedirect(reverse("mycompany"))

@login_required
def get_mycompany_details(request):
    company_id = request.GET.get("id")
    if company_id:
        company = get_object_or_404(MyCompanyModel, pk=company_id)
        data = {
            "name": company.name,
            "address": company.address,
            "postcode": company.postcode,
            "city": company.city,
            "nation": company.nation,
            "telephone": company.telephone,
            "email": company.email,
            "btw": company.btw,
            "kvk": company.kvk,
            "iban": company.iban,
            "is_active": company.is_active
        }

        return JsonResponse(data)
    else:
        return JsonResponse({"error": "No company"}, status=404)