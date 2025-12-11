from django.db import models, transaction
from datetime import datetime
from django.db.models import Max


def current_year():
    return datetime.now().year


# Category Model for costs
class CategoryModel(models.Model):
    category = models.CharField(max_length=150)

    def __str__(self):
        return self.category

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


# Description Model for costs
class DescriptionModel(models.Model):
    categoryID = models.ForeignKey(CategoryModel, related_name="descriptions", on_delete=models.CASCADE)
    description = models.CharField(max_length=250)

    def __str__(self):
        return f"{self.categoryID.category}:  {self.description}"

    class Meta:
        verbose_name = "Description"
        verbose_name_plural = "Descriptions"


# Costs Model
class CostModel(models.Model):
    reference_id = models.CharField(max_length=11, editable=False, unique=True, null=True)
    cost_date = models.DateField()
    category_id = models.ForeignKey(CategoryModel, on_delete=models.CASCADE)
    description_id = models.ForeignKey(DescriptionModel, on_delete=models.CASCADE)
    euro_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_credit = models.BooleanField(default=False)
    cost_note = models.CharField(max_length=250, blank=True, null=True)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.reference_id:
                last_qtn = CostModel.objects.select_for_update().aggregate(
                    Max('reference_id'))
                last_qtn_number = int(last_qtn['reference_id__max'][8:]) if last_qtn[
                    'reference_id__max'] else 0
                self.reference_id = f"CST{current_year()}-{str(last_qtn_number + 1).zfill(3)}"  #
                print(f'Assigned reference_id: {self.reference_id}')
        super().save(*args, **kwargs)

    def __str__(self):
        category = self.category_id.category if self.category_id else "No category"
        description = self.description_id.description if self.description_id else "No description"
        return f"{self.cost_date}: € {self.euro_amount} {self.is_credit}"

    class Meta:
        verbose_name = "Cost"
        verbose_name_plural = "Costs"