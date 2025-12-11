from django.db import models


class CustomerModel(models.Model):
    name = models.CharField(max_length=250)
    address = models.CharField(max_length=250, blank=True, null=True)
    postcode = models.CharField(max_length=10, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    nation = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    btw = models.CharField(max_length=20, blank=True, null=True)
    kvk = models.CharField(max_length=20, blank=True, null=True)
    bankaccountname = models.CharField(max_length=80, blank=True, null=True)
    iban = models.CharField(max_length=34, blank=True, null=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"