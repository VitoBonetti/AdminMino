import openpyxl
from datetime import datetime
from django.shortcuts import (
    render,
    get_object_or_404,
    reverse
)
from django.db.models import (
    Sum,
    Case,
    When,
    DecimalField
)
from costs.models import (
    CategoryModel,
    DescriptionModel,
    CostModel
)
from costs.forms import (
    CategoryForm,
    DescriptionForm,
    CostForm
)
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


# Category Views
class CategoryView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        category_id = request.GET.get("id", None)
        if category_id:
            category = get_object_or_404(CategoryModel, pk=category_id)
            form_category = CategoryForm(instance=category)
        else:
            form_category = CategoryForm()

        categories = CategoryModel.objects.all().order_by("category")

        context = {
            "form_category": form_category,
            "categories": categories,
        }

        return render(request, "costs/categories.html", context=context)

    def post(self, request, *args, **kwargs):
        category_id = request.POST.get("id", None)
        is_active = request.POST.get("is_active", "off") == "on"  # Manually handle the checkbox
        if category_id:
            category = get_object_or_404(CategoryModel, pk=category_id)
            form_category = CategoryForm(request.POST, instance=category)
        else:
            form_category = CategoryForm(request.POST)

        if form_category.is_valid():
            instance = form_category.save(commit=False)
            instance.is_active = is_active  # Ensure is_active reflects the checkbox's state
            instance.save()
            form_category = CategoryForm()

        categories = CategoryModel.objects.all().order_by("category")

        context = {
            "form_category": form_category,
            "categories": categories,
        }

        return render(request, "costs/categories.html", context=context)


class CategoryAutocompleteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        categories = CategoryModel.objects.filter(category__icontains=query).order_by("category")
        categories_list = [
            {
                'id': category.id,
                'category': category.category,
                'descriptions': [description.description for description in category.descriptions.all()]
            }
            for category in categories
        ]
        return JsonResponse(categories_list, safe=False)


class DeleteCategoryView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        category_id = self.kwargs['pk']
        category = get_object_or_404(CategoryModel, pk=category_id)
        category.delete()
        return HttpResponseRedirect(reverse('categories'))


# Descriptions Views
class DescriptionView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        description_id = request.GET.get('id', None)
        if description_id:
            description = get_object_or_404(DescriptionModel, pk=description_id)
            form_description = DescriptionForm(instance=description)
        else:
            form_description = DescriptionForm()

        descriptions = DescriptionModel.objects.all().order_by('categoryID__category', 'description')

        context = {
            "form_description": form_description,
            "descriptions": descriptions,
        }

        return render(request, "costs/descriptions.html", context=context)

    def post(self, request, *args, **kwargs):
        description_id = request.POST.get('id', None)
        if description_id:
            description = get_object_or_404(DescriptionModel, pk=description_id)
            form_description = DescriptionForm(request.POST, instance=description)
        else:
            form_description = DescriptionForm(request.POST)

        if form_description.is_valid():
            form_description.save()
            form_description = DescriptionForm()

        descriptions = DescriptionModel.objects.all().order_by('categoryID__category', 'description')

        context = {
            "form_description": form_description,
            "descriptions": descriptions,
        }

        return render(request, "costs/descriptions.html", context=context)


@method_decorator(csrf_exempt, name='dispatch')
class DeleteDescriptionView(LoginRequiredMixin, View):
    def delete(self, request, *args, **kwargs):
        description_id = self.kwargs['pk']
        description = get_object_or_404(DescriptionModel, pk=description_id)
        description.delete()
        return JsonResponse({"status": "success"})


@login_required
def get_description(request, description_id):
    description = get_object_or_404(DescriptionModel, pk=description_id)
    data = {
        "id": description.id,
        "description": description.description,
        "category_id": description.categoryID_id
    }
    return JsonResponse(data)


@login_required
def get_descriptions_by_category(request, category_id):
    query = request.GET.get('q', '')
    descriptions = DescriptionModel.objects.filter(
        categoryID_id=category_id,
        description__icontains=query
    ).order_by('description')
    descriptions_list = [
        {
            "id": description.id,
            "description": description.description,
            "category_id": description.categoryID_id,
            "category": description.categoryID.category
        }
        for description in descriptions
    ]
    return JsonResponse(descriptions_list, safe=False)


class CostView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            category_id = request.GET.get('category_id')
            description_id = request.GET.get('description_id')

            if description_id:
                costs = CostModel.objects.filter(description_id=description_id).order_by("-cost_date")
            elif category_id:
                costs = CostModel.objects.filter(description_id__categoryID__id=category_id).order_by("-cost_date")
            else:
                costs = CostModel.objects.all().order_by("-cost_date")

            costs_data = []
            for cost in costs:
                costs_data.append({
                    'reference_id': cost.reference_id,
                    'cost_date': cost.cost_date.strftime("%d-%m-%Y"),
                    'category': cost.description_id.categoryID.category
                    if cost.description_id and cost.description_id.categoryID
                       and cost.description_id.categoryID.category
                    else '',
                    'description': cost.description_id.description
                    if cost.description_id and cost.description_id.description
                    else '',
                    'euro_amount': cost.euro_amount,
                    'is_credit': cost.is_credit,
                    'cost_note': cost.cost_note,
                    'id': cost.id,
                })
            return JsonResponse(costs_data, safe=False)

        cost_id = request.GET.get('id', None)

        if cost_id:
            cost = get_object_or_404(CostModel, pk=cost_id)
            form = CostForm(instance=cost)
        else:
            form = CostForm()

        totals = CostModel.objects.aggregate(
            credit_sum=Sum(
                Case(When(is_credit=True, then='euro_amount'), output_field=DecimalField())
            ),
            debit_sum=Sum(
                Case(When(is_credit=False, then='euro_amount'), output_field=DecimalField())
            )
        )

        categories = CategoryModel.objects.all()
        descriptions = DescriptionModel.objects.all()
        costs = CostModel.objects.all().order_by("-cost_date")

        credit_sum = totals['credit_sum']
        debit_sum = totals['debit_sum']

        if credit_sum is None:
            credit_sum = 0
        if debit_sum is None:
            debit_sum = 0

        balace_sum = (credit_sum - debit_sum)

        context = {
            'form': form,
            'categories': categories,
            'descriptions': descriptions,
            'costs': costs,
            "credit_sum": round(credit_sum, 2) if credit_sum is not None else None,
            "debit_sum": round(debit_sum, 2) if debit_sum is not None else None,
            "balace_sum": round(balace_sum, 2) if balace_sum is not None else None,
        }

        return render(request, 'costs/costs.html', context=context)

    def post(self, request, *args, **kwargs):
        # check if 'category_id' and 'description_id' has more than one value
        if len(request.POST.getlist('category_id')) > 1 or len(request.POST.getlist('description_id')) > 1:
            # remove 'None' from the list
            category_ids = [id for id in request.POST.getlist('category_id') if id != 'None']
            description_ids = [id for id in request.POST.getlist('description_id') if id != 'None']

            # get first valid value
            if category_ids:
                category_id = category_ids[0]
            if description_ids:
                description_id = description_ids[0]

            # build new POST data dict without 'None' values
            new_post = request.POST.copy()
            new_post.setlist('category_id', [category_id])
            new_post.setlist('description_id', [description_id])

            # replace the POST data with the new one
            request.POST = new_post

        cost_id = request.POST.get('id', None)

        if cost_id:
            cost = get_object_or_404(CostModel, pk=cost_id)
            form = CostForm(request.POST, instance=cost)
        else:
            form = CostForm(request.POST)

        if form.is_valid():
            form.save()

            form = CostForm()

        totals = CostModel.objects.aggregate(
            credit_sum=Sum(
                Case(When(is_credit=True, then='euro_amount'), output_field=DecimalField())
            ),
            debit_sum=Sum(
                Case(When(is_credit=False, then='euro_amount'), output_field=DecimalField())
            )
        )

        categories = CategoryModel.objects.all()
        descriptions = DescriptionModel.objects.all()
        # Fetch costs and apply pagination
        costs = CostModel.objects.all()

        credit_sum = totals['credit_sum']
        debit_sum = totals['debit_sum']

        if credit_sum is None:
            credit_sum = 0
        if debit_sum is None:
            debit_sum = 0

        balace_sum = (credit_sum - debit_sum)

        context = {
            'form': form,
            'categories': categories,
            'descriptions': descriptions,
            'costs': costs,
            "credit_sum": round(credit_sum, 2) if credit_sum is not None else None,
            "debit_sum": round(debit_sum, 2) if debit_sum is not None else None,
            "balace_sum": round(balace_sum, 2) if balace_sum is not None else None,
        }

        return render(request, 'costs/costs.html', context=context)


class DeleteCostView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cost_id = self.kwargs['pk']
        cost = get_object_or_404(CostModel, pk=cost_id)
        cost.delete()
        return HttpResponseRedirect(reverse('costs'))


@login_required
def fetch_descriptions(request, category_id):
    category = get_object_or_404(CategoryModel, pk=category_id)
    descriptions = DescriptionModel.objects.filter(categoryID=category)
    data = [{"id": description.id, "description": description.description} for description in descriptions]
    return JsonResponse({"data": data})


@login_required
def export_costs_excel(request):
    # 1. Create a workbook and sheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Costs Export"

    # 2. Define the headers
    headers = [
        "Reference ID",
        "Date",
        "Category",
        "Description",
        "Amount (€)",
        "Type",
        "Note"
    ]
    ws.append(headers)

    # 3. Fetch data efficiently
    costs = CostModel.objects.all().select_related('category_id', 'description_id').order_by('-cost_date')

    # 4. Write data to rows
    for cost in costs:
        category_name = cost.category_id.category if cost.category_id else "N/A"
        description_name = cost.description_id.description if cost.description_id else "N/A"
        cost_type = "Credit" if cost.is_credit else "Debit"

        row = [
            cost.reference_id,
            cost.cost_date,
            category_name,
            description_name,
            cost.euro_amount,
            cost_type,
            cost.cost_note
        ]
        ws.append(row)

    # 5. Generate Filename with Timestamp
    # Format: costs_export_YYYY-MM-DD_HH-MM-SS.xlsx
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"costs_export_{timestamp}.xlsx"

    # 6. Prepare the response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    # Update the Content-Disposition with the dynamic filename
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # 7. Save workbook to response
    wb.save(response)
    return response
