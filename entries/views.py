from django.shortcuts import (
    render,
    get_object_or_404,
    reverse,
    redirect
)
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import (
    Case,
    When,
    Value,
    BooleanField
)
from entries.models import EntryModel, EntryProductsModel
from entries.forms import EntryForm, EntryProductsFormSet, EntryModelForm, EntryProductsFormSetNoExtra
from suppliers.models import SupplierModel, LoadingAddressModel
from mycompany.models import MyCompanyModel
from customers.models import CustomerModel
from datetime import date
from django.http import FileResponse
from entries.algemene import (
    algemene_title,
    algemene_commission,
    algemene_invoice,
    algemene_offerte,
    footer_text
)
from decimal import Decimal
from django_weasyprint import WeasyTemplateResponseMixin
from django_weasyprint.views import WeasyTemplateResponse


class EntriesInLineView(LoginRequiredMixin):
    form_class = EntryForm
    model = EntryModel
    template_name = "entries/edit-entry.html"

    def form_valid(self, form):
        context = self.get_context_data()
        named_formsets = context['named_formsets']

        if form.is_valid() and all((x.is_valid() for x in named_formsets.values())):
            self.object = form.save()
            for name, formset in named_formsets.items():
                formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
                if formset_save_func is not None:
                    formset_save_func(formset)
                else:
                    formset.instance = self.object
                    formset.save()
            return redirect('entries')
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def formset_product_valid(self, formset):
        products = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for product in products:
            product.entry_id = self.object
            product.save()


class NewEntryView(EntriesInLineView, CreateView):
    def form_valid(self, form):
        self.object = form.save()
        product_formset = EntryProductsFormSet(self.request.POST, instance=self.object, prefix='products')

        if not product_formset.is_valid():
            return self.form_invalid(form)

        self.object.save()  # Now, actually save the object to DB
        product_formset.instance = self.object
        product_formset.save()
        self.object.update_totals()  # Update totals after saving related objects
        return HttpResponseRedirect(reverse('entries'))  # Redirect to your success URL

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['suppliers'] = SupplierModel.objects.filter(is_active=True)
        context['companies'] = MyCompanyModel.objects.filter(is_active=True)
        context['customers'] = CustomerModel.objects.filter(is_active=True)

        if self.request.POST:
            context['named_formsets'] = {
                "products": EntryProductsFormSet(self.request.POST, prefix='products')
            }
        else:
            context['named_formsets'] = {
                "products": EntryProductsFormSet(prefix='products')
            }

        if self.object and self.object.supplier_id:
            loading_addresses = LoadingAddressModel.objects.filter(supplier_id=self.object.supplier_id)
            context['loading_addresses'] = loading_addresses

        return context


class UpdateEntryView(EntriesInLineView, UpdateView):
    model = EntryModel
    form_class = EntryModelForm

    def get_initial(self):
        initial = super(UpdateEntryView, self).get_initial()
        if self.object:
            initial['company_id'] = self.object.company_id.id if self.object.company_id else None
            initial['customer_id'] = self.object.customer_id.id if self.object.customer_id else None
            initial['supplier_id'] = self.object.supplier_id.id if self.object.supplier_id else None
        return initial

    def form_valid(self, form):
        self.object = form.save()
        product_formset = EntryProductsFormSet(self.request.POST, instance=self.object, prefix='products')

        if not product_formset.is_valid():
            return self.form_invalid(form)

        self.object.save()  # Now, actually save the object to DB
        product_formset.instance = self.object
        product_formset.save()
        self.object.update_totals()  # Update totals after saving related objects
        return HttpResponseRedirect(reverse('entries'))  # Redirect to your success URL

    def get_context_data(self, **kwargs):
        context = super(UpdateEntryView, self).get_context_data(**kwargs)
        context['suppliers'] = SupplierModel.objects.filter(is_active=True)
        context['companies'] = MyCompanyModel.objects.filter(is_active=True)
        context['customers'] = CustomerModel.objects.filter(is_active=True)
        context['entry'] = self.object

        if self.request.method == 'POST':
            context['named_formsets'] = {
                "products": EntryProductsFormSetNoExtra(self.request.POST, instance=self.object, prefix='products')
            }
        else:
            context['named_formsets'] = {
                "products": EntryProductsFormSetNoExtra(instance=self.object, prefix='products')
                # "products": EntryProductsFormSet(instance=self.object, prefix='products',
                # queryset=EntryProductsModel.objects.filter(entry_id=self.object), extra=0)
            }

        if self.object and self.object.supplier_id:
            loading_addresses = LoadingAddressModel.objects.filter(supplier_id=self.object.supplier_id)
            context['loading_addresses'] = loading_addresses

        if self.object is not None:
            context['form'].initial['company_id'] = self.object.company_id
            context['form'].initial['customer_id'] = self.object.customer_id
            context['form'].initial['supplier_id'] = self.object.supplier_id

        return context


class EntryView(LoginRequiredMixin, ListView):
    model = EntryModel
    template_name = "entries/entries.html"
    context_object_name = "entries"

    def get_queryset(self):
        queryset = super().get_queryset()

        queryset = queryset.annotate(
            overdue_unpaid=Case(
                When(overdue_date__lt=timezone.now().date(), is_paid=False, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
            unpaid=Case(
                When(is_paid=False, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            )
        ).order_by('-overdue_unpaid', '-unpaid', 'overdue_date')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = date.today()
        return context


@login_required
def delete_entry(request, pk):
    try:
        entry = EntryModel.objects.get(id=pk)
    except EntryModel.DoesNotExist:
        messages.success(request, 'Object does not exist')

    return redirect('edit-entry', pk=entry.entry_id.id)


class DeleteEntryView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        entry_id = self.kwargs['pk']
        entry = get_object_or_404(EntryModel, pk=entry_id)
        entry.delete()
        return HttpResponseRedirect(reverse('entries'))


@login_required
def EntryDetailView(request, pk):
    entry = get_object_or_404(EntryModel, id=pk)
    products = EntryProductsModel.objects.filter(entry_id=pk)

    # Add transport data to context
    transport = {
        'transport_gross': entry.transport_gross,
        'transport_bereken': entry.transport_bereken,
        'transport_price_for_ton': entry.transport_price_for_ton,
        'transport_diesel_toeslag': entry.transport_diesel_toeslag,
        'transport_extra_stop': entry.transport_extra_stop,
        'transport_extra_stop_cost': entry.transport_extra_stop_cost,
        'transport_total_no_btw': entry.transport_total_no_btw
    }

    algemene = {
        "algemene_title": algemene_title,
        "algemene_offerte": algemene_offerte,
        "algemene_invoice": algemene_invoice,
        "algemene_commission": algemene_commission,
        # "footer_text": footer_text
    }

    if entry.is_commission:
        btw_calc = 0
    else:
        # Ensure btw_total and no_btw_total are not None before subtraction
        btw_total = entry.final_total if entry.final_total is not None else Decimal('0')
        no_btw_total = entry.temp_no_btw_total if entry.temp_no_btw_total is not None else Decimal('0')

        btw_calc = btw_total - no_btw_total

    total_discount = 0
    if entry.discount > 0:
        total_discount = entry.btw_total - entry.btw_total_discount

    context = {
        "entry": entry,
        "products": products,
        "btw_calc": btw_calc,
        "transport": transport,
        "algemene": algemene,
        "total_discount": total_discount,
    }

    return render(request, "entries/entry-detail.html", context=context)


class CommissionEntryView(LoginRequiredMixin, View):
    def get(self, request):
        commission_entries = EntryModel.objects.filter(is_commission=True).annotate(
            overdue_unpaid=Case(
                When(is_paid=False, overdue_date__lt=timezone.now().date(), then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
            unpaid=Case(
                When(is_paid=False, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            )
        ).order_by('-overdue_unpaid', '-unpaid', 'overdue_date')

        context = {
            "commission_entries": commission_entries,
            "today": date.today(),
        }

        return render(request, "entries/commissions.html", context=context)


class InvoiceEntryView(LoginRequiredMixin, View):
    def get(self, request):
        invoice_entries = EntryModel.objects.filter(is_invoice=True).annotate(
            overdue_unpaid=Case(
                When(is_paid=False, overdue_date__lt=timezone.now().date(), then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
            unpaid=Case(
                When(is_paid=False, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            )
        ).order_by('-overdue_unpaid', '-unpaid', 'overdue_date')

        context = {
            "invoice_entries": invoice_entries,
            "today": date.today(),
        }

        return render(request, "entries/invoices.html", context=context)


class QuotationEntryView(LoginRequiredMixin, View):
    def get(self, request):
        quotation_entries = EntryModel.objects.filter(is_quotation=True, is_invoice=False).annotate(
            overdue_unpaid=Case(
                When(is_paid=False, overdue_date__lt=timezone.now().date(), then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
            unpaid=Case(
                When(is_paid=False, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            )
        ).order_by('-overdue_unpaid', '-unpaid', 'overdue_date')

        context = {
            "quotation_entries": quotation_entries,
            "today": date.today(),
        }

        return render(request, "entries/quotations.html", context=context)


@login_required
def get_loading_addresses(request):
    supplier_id = request.GET.get('supplier_id', None)
    data = list(LoadingAddressModel.objects.filter(supplier_id=supplier_id).values())
    return JsonResponse(data, safe=False)


class EntryDetailPDFView(LoginRequiredMixin, WeasyTemplateResponseMixin, DetailView):
    model = EntryModel
    template_name = "entries/entry-detail.html"

    # This method dynamically sets the PDF filename
    def get_pdf_filename(self):
        entry = self.get_object()
        if entry.is_quotation and not entry.is_invoice:
            pdf_filename = f"{entry.quotation_reference}.pdf"
        else:
            pdf_filename = f"{entry.invoice_reference}.pdf"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entry = self.get_object()
        products = EntryProductsModel.objects.filter(entry_id=entry.id)

        # Add transport data to context
        transport = {
            'transport_gross': entry.transport_gross,
            'transport_bereken': entry.transport_bereken,
            'transport_price_for_ton': entry.transport_price_for_ton,
            'transport_diesel_toeslag': entry.transport_diesel_toeslag,
            'transport_extra_stop': entry.transport_extra_stop,
            'transport_extra_stop_cost': entry.transport_extra_stop_cost,
            'transport_total_no_btw': entry.transport_total_no_btw
        }

        algemene = {
            "algemene_title": algemene_title,
            "algemene_offerte": algemene_offerte,
            "algemene_invoice": algemene_invoice,
            "algemene_commission": algemene_commission,
            "footer_text": footer_text
        }

        if entry.is_commission:
            btw_calc = 0
        else:
            # Ensure btw_total and no_btw_total are not None before subtraction
            btw_total = entry.final_total if entry.final_total is not None else Decimal('0')
            no_btw_total = entry.temp_no_btw_total if entry.temp_no_btw_total is not None else Decimal('0')

            btw_calc = btw_total - no_btw_total

        total_discount = 0
        if entry.discount > 0:
            total_discount = entry.btw_total - entry.btw_total_discount

        context = {
            "entry": entry,
            "products": products,
            "btw_calc": btw_calc,
            "transport": transport,
            "algemene": algemene,
            "total_discount": total_discount,
        }

        return context


@login_required
def entry_detail_pdf(request, pk):
    entry = get_object_or_404(EntryModel, pk=pk)
    response = EntryDetailPDFView.as_view()(request, pk=pk)
    return response

