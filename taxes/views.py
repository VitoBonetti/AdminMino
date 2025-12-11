from django.shortcuts import render
from django.db.models import Sum, Case, When, DecimalField, F
from django.http import JsonResponse
from django.db.models.functions import ExtractYear
from costs.models import CostModel
from entries.models import EntryModel
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from decimal import Decimal, ROUND_HALF_UP


@login_required
def taxes_view(request):
    years = EntryModel.objects.annotate(year=ExtractYear("overdue_date")).values("year").distinct().order_by("year")
    context = {
        "years": [year["year"] for year in years]
    }

    return render(request, "taxes/taxes.html", context=context)


@login_required
def fetch_quarters(request):
    year = request.GET.get("year")
    if year:
        quarters = [
            {"quarter": 1, "name": "Q1 (Jan - Mar)"},
            {"quarter": 2, "name": "Q2 (Apr - Jun)"},
            {"quarter": 3, "name": "Q3 (Jul - Sep)"},
            {"quarter": 4, "name": "Q4 (Oct - Dec)"},
        ]
        return JsonResponse(quarters, safe=False)
    return JsonResponse([], safe=False)


@login_required
def fetch_cost_view(request):
    year = request.GET.get("year")
    quarter = request.GET.get("quarter")
    if year and quarter:
        quarter_map = {
            "1": (1, 3),
            "2": (4, 6),
            "3": (7, 9),
            "4": (10, 12),
        }

        start_month, end_month = quarter_map.get(quarter, (1, 12))

        # Filter date range for EntryModel
        entry_data = EntryModel.objects.filter(
            overdue_date__year=year,
            overdue_date__month__gte=start_month,
            overdue_date__month__lte=end_month,
            is_paid=True
        ).aggregate(entry_total_cost=Sum("final_total")) or {"entry_total_cost": 0}

        # Filter date range for CostModel
        general_cost_data = CostModel.objects.filter(
            cost_date__year=year,
            cost_date__month__gte=start_month,
            cost_date__month__lte=end_month,
        )

        # Aggregations for CostModel
        # basic_cost_data all the costs excluding the salary, taxes, and bank interest
        basic_cost_data = general_cost_data.exclude(
            category_id__category="GENERAL", description_id__description="Salary"
        ).exclude(
            category_id__category="TAX"
        ).exclude(
            category_id__category="GENERAL", description_id__description="ABNAmro", is_credit=True
        ).aggregate(basic_cost=Sum("euro_amount")) or {"basic_cost": 0}

        # bank_interest_data including only the category GENERAL, description ABNAmro and is_credit is True
        bank_interest_data = general_cost_data.filter(
            category_id__category="GENERAL", description_id__description="ABNAmro", is_credit=True
        ).aggregate(bank_interest=Sum("euro_amount")) or {"bank_interest": 0}

        # total_salary_data including only category_id__name="GENERAL", description_id__name="SALARY"
        total_salary_data = general_cost_data.filter(
            category_id__category="GENERAL", description_id__description="Salary"
        ).aggregate(total_salary=Sum("euro_amount")) or {"total_salary": 0}

        # total_tax_data including only category_id__name="TAX", is_Credit true positive value,
        # is_credit false negative value.
        total_tax_data = general_cost_data.filter(
            category_id__category="TAX"
        ).aggregate(
            total_tax=Sum(
                Case(
                    When(is_credit=True, then=F("euro_amount")),
                    When(is_credit=False, then=-F("euro_amount")),
                    output_field=DecimalField(),
                ),
                output_field=DecimalField()
            )
        ) or {"total_tax": 0}

        # Extract values from the dictionaries and handle None values
        entry_total_cost = Decimal(entry_data.get("entry_total_cost") or 0).quantize(Decimal('0.00'),
                                                                                     rounding=ROUND_HALF_UP)
        basic_cost = Decimal(basic_cost_data.get("basic_cost") or 0).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        bank_interest = Decimal(bank_interest_data.get("bank_interest") or 0).quantize(Decimal('0.00'),
                                                                                       rounding=ROUND_HALF_UP)
        total_salary = Decimal(total_salary_data.get("total_salary") or 0).quantize(Decimal('0.00'),
                                                                                    rounding=ROUND_HALF_UP)
        total_tax = Decimal(total_tax_data.get("total_tax") or 0).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

        # Perform calculations
        first_step = basic_cost - bank_interest
        second_step = first_step + total_tax
        third_step = entry_total_cost - second_step
        tax = third_step * Decimal('0.45')
        after_tax = third_step - tax
        quarter_safe = after_tax - total_salary

        # Round the results to two decimal places
        first_step = first_step.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        second_step = second_step.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        third_step = third_step.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        tax = tax.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        after_tax = after_tax.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        quarter_safe = quarter_safe.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

        response_data = {
            "entry_data": entry_total_cost,
            "basic_cost": basic_cost,
            "bank_interest": bank_interest,
            "total_salary": total_salary,
            "total_tax": total_tax,
            "first_step": first_step,
            "second_step": second_step,
            "third_step": third_step,
            "tax": tax,
            "after_tax": after_tax,
            "quarter_safe": quarter_safe
        }

        return JsonResponse(response_data)
    return JsonResponse({})