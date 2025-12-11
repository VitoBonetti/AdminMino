from django.db import models, transaction
from mycompany.models import MyCompanyModel
from customers.models import CustomerModel
from suppliers.models import SupplierModel, LoadingAddressModel
from datetime import datetime
from datetime import timedelta
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Q, Max
from decimal import Decimal


def current_year():
    return datetime.now().year


# Create your models here.
class EntryModel(models.Model):
    date = models.DateField()
    overdue_date = models.DateField(blank=True, null=True)
    company_id = models.ForeignKey(MyCompanyModel, on_delete=models.CASCADE, blank=True, null=True, default=None)
    customer_id = models.ForeignKey(CustomerModel, on_delete=models.CASCADE, blank=True, null=True, default=None)
    supplier_id = models.ForeignKey(SupplierModel, on_delete=models.CASCADE, blank=True, null=True, default=None)
    loading_address = models.ForeignKey(LoadingAddressModel, on_delete=models.SET_NULL, blank=True, null=True)
    quotation_reference = models.CharField(max_length=11, editable=False, unique=True, null=True)
    invoice_reference = models.CharField(max_length=11, editable=False, unique=True, null=True)
    is_invoice = models.BooleanField(default=False)
    is_commission = models.BooleanField(default=False)
    is_quotation = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    pallets_quantity = models.IntegerField(default=0, blank=True, null=True)
    pallets_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pallets_total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    pallets_notes = models.CharField(max_length=500, blank=True, null=True)
    transport_gross = models.IntegerField(default=0, blank=True, null=True)
    transport_bereken = models.IntegerField(default=0, editable=False, blank=True, null=True)
    transport_price_for_ton = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transport_diesel_toeslag = models.IntegerField(default=0, validators=[MaxValueValidator(100), MinValueValidator(0)])
    transport_extra_stop = models.IntegerField(default=0, validators=[MaxValueValidator(99), MinValueValidator(0)])
    transport_extra_stop_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transport_total_no_btw = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    transport_total_btw = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    temp_no_btw_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, editable=False)
    no_btw_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    btw_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount = (
        models.IntegerField(default=0, validators=[MaxValueValidator(99), MinValueValidator(0)], blank=True, null=True))
    btw_total_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    final_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    loading_info = models.CharField(max_length=300, blank=True, null=True)
    notes = models.CharField(max_length=500, blank=True, null=True)

    def update_transport_bereken(self):
        # Update the transport_bereken based on transport_gross
        if 0 < int(self.transport_gross) <= 1000:
            self.transport_bereken = 1000
        elif int(self.transport_gross) <= 0:
            self.transport_bereken = 0
        else:
            # Round up to the nearest thousand
            self.transport_bereken = ((int(self.transport_gross) - 1) // 1000 + 1) * 1000

    def update_totals(self):
        related_products = EntryProductsModel.objects.filter(entry_id=self)
        self.no_btw_total = sum(product.total for product in related_products)  # this is including already discount

        if self.is_commission:
            self.btw_total = self.no_btw_total
            self.final_total = self.no_btw_total
            self.temp_no_btw_total = self.no_btw_total
        elif self.is_quotation or self.is_invoice:

            # Update transport_bereken
            self.update_transport_bereken()

            # Calculate transport_total_no_btw
            transport_cost = float(self.transport_price_for_ton) * (self.transport_bereken / 1000)
            diesel_toeslag = transport_cost * (int(self.transport_diesel_toeslag) / 100)
            self.transport_total_no_btw = transport_cost + diesel_toeslag + float(self.transport_extra_stop_cost)

            # Convert transport_total_no_btw to Decimal
            transport_total_no_btw_decimal = Decimal(str(self.transport_total_no_btw))

            # Add transport_total_no_btw to temp_no_btw_total 2
            self.temp_no_btw_total = transport_total_no_btw_decimal + self.no_btw_total

            #
            #
            # self.btw_total = self.no_btw_total * Decimal('1.21')
            # self.transport_total_btw = transport_total_no_btw_decimal * Decimal('1.21')
            #
            # self.btw_total_discount = self.btw_total

            # if self.discount:
            #     discount_rate = self.discount / 100
            #     self.btw_total_discount = self.btw_total * (Decimal('1') - Decimal(discount_rate))

            if self.pallets_quantity > 0 and self.pallets_price > 0:
                self.pallets_total_price = self.pallets_quantity * self.pallets_price
            else:
                self.pallets_total_price = 0

            self.temp_no_btw_total += self.pallets_total_price

            self.final_total = self.temp_no_btw_total * Decimal('1.21')

        self.save()

    def save(self, *args, **kwargs):
        # Check if the instance already exists in the database
        instance_exists = self.pk is not None
        status_changed_to_invoice = False
        if instance_exists:
            original = EntryModel.objects.get(pk=self.pk)
            was_quotation = original.is_quotation and not original.is_invoice
            # Check if status changed from quotation to invoice
            status_changed_to_invoice = was_quotation and self.is_invoice
        else:
            was_quotation = self.is_quotation and not self.is_invoice

        # Update the overdue date based on status change or date modification
        if not self.overdue_date or status_changed_to_invoice or (instance_exists and self.date != original.date):
            # new_overdue_days = 30 if self.is_invoice else 7
            new_overdue_days = 30
            base_date = timezone.now() if status_changed_to_invoice else (self.date or timezone.now())
            self.overdue_date = base_date + timedelta(days=new_overdue_days)

        if self.is_paid:
            self.overdue_date = timezone.now().date()

        with transaction.atomic():
            current_year_str = str(current_year())
            if self.is_quotation and not self.quotation_reference:
                # Fetch all quotation_references for the current year, then extract and convert the numeric parts
                last_qtn_refs = EntryModel.objects.filter(
                    quotation_reference__startswith=f"QTN{current_year_str}"
                ).order_by('-quotation_reference').values_list('quotation_reference', flat=True)

                max_number = 0
                for ref in last_qtn_refs:
                    try:
                        # Attempt to extract the numeric part of each reference
                        number_part = int(ref.split('-')[-1])
                        max_number = max(max_number, number_part)
                    except ValueError:
                        # Handle cases where the reference format is unexpected
                        continue

                # Determine the next quotation number
                new_qtn_number = max_number + 1
                self.quotation_reference = f"QTN{current_year_str}-{str(new_qtn_number).zfill(3)}"
                print(f'Assigned quotation_reference: {self.quotation_reference}')

            if (self.is_invoice or (self.is_commission and not self.is_quotation)) and not self.invoice_reference:
                last_inv = EntryModel.objects.select_for_update().filter(
                    Q(is_invoice=True) | Q(is_commission=True, is_quotation=False),
                    invoice_reference__startswith=f"INV{current_year_str}"
                ).aggregate(Max('invoice_reference'))
                last_inv_number = int(last_inv['invoice_reference__max'][8:]) if last_inv[
                    'invoice_reference__max'] else 0
                self.invoice_reference = f"INV{current_year_str}-{str(last_inv_number + 1).zfill(3)}"
                print(f'Assigned invoice_reference: {self.invoice_reference}')

        super().save(*args, **kwargs)

    def is_overdue(self):
        overdue = self.overdue_date < timezone.now().date()
        print(f'Entry with id={self.id} overdue status: {overdue}')
        return overdue

    def __str__(self):
        if self.is_quotation and self.is_invoice:
            return (f"{self.quotation_reference} - {self.invoice_reference} |"
                    f" Date: {self.date} Overdue: {self.overdue_date} -- € {self.btw_total_discount}")
        elif self.is_quotation and not self.is_invoice:
            return (f"{self.quotation_reference} | "
                    f"Date: {self.date} Overdue: {self.overdue_date} -- € {self.btw_total_discount}")
        elif self.is_invoice and not self.is_quotation:
            return (f"{self.invoice_reference} | "
                    f"Date: {self.date} Overdue: {self.overdue_date} -- € {self.btw_total_discount}")
        elif self.is_commission and not self.is_quotation and not self.is_invoice:
            return (f"{self.invoice_reference} | "
                    f"Date: {self.date} Overdue: {self.overdue_date} -- € {self.btw_total_discount}")

    class Meta:
        verbose_name = "Entry"
        verbose_name_plural = "Entries"


class EntryProductsModel(models.Model):
    UNITY_CHOICES = [
        ("m2", "m2"),
        ("ml", "ml"),
        ("bx", "bx"),
        ("st", "st"),
        ("fg", "fg"),
    ]

    entry_id = models.ForeignKey(EntryModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=250, blank=True, null=True)
    description = models.CharField(max_length=250, blank=True, null=True)
    quantity = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    unity = models.CharField(max_length=2, choices=UNITY_CHOICES, default="m2")
    unity_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        base_total = self.quantity * self.unity_price
        if self.discount > 0:
            discount_amount = base_total * (self.discount / 100)
            self.total = base_total - discount_amount
        else:
            self.total = base_total
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
