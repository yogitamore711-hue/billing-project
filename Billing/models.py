from django.db import models
from django.contrib.auth.models import User
from django import forms

class ShopProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=200, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    gstin = models.CharField(max_length=20, blank=True)
    upi_id = models.CharField(max_length=100, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=30, blank=True)
    ifsc_code = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return self.shop_name

class Bill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    invoice_no = models.CharField(max_length=50, unique=True)
    customer_phone = models.CharField(max_length=15, null=True, blank=True)
    customer_name = models.CharField(max_length=200, null=True, blank=True)

    total_amount = models.FloatField(default=0)
    cgst = models.FloatField(default=0)
    sgst = models.FloatField(default=0)
    grand_total = models.FloatField(default=0)

    PAYMENT_CHOICES = [
        ("Cash", "Cash"),
        ("Online", "Online"),
    ]

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default="Cash"
    )

    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)  # only for Online
    created_at = models.DateTimeField(auto_now_add=True)
    pdf = models.FileField(upload_to='bills/', blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.invoice_no

class BillItem(models.Model):
    bill = models.ForeignKey(
        Bill,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product_name = models.CharField(max_length=200)
    hsn = models.CharField(max_length=20, blank=True)
    qty = models.PositiveIntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def amount(self):
        return self.qty * self.rate

    def __str__(self):
        return self.product_name

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['customer_name', 'customer_phone', 'payment_method']

class BillItemForm(forms.ModelForm):
    class Meta:
        model = BillItem
        fields = ['product_name', 'hsn', 'qty', 'rate']
        


