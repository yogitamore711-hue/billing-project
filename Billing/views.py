from urllib import request
import os ,uuid
import base64
import qrcode
from io import BytesIO
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Bill
from django.http import HttpResponse
from fpdf import FPDF
from django.conf import settings
from django.contrib import messages
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from .models import ShopProfile, Bill, BillItem
from django.http import HttpResponse
import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.core.files import File
import random
import string
from django.core.mail import send_mail

# Signup View
def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        # Check empty fields
        if not username or not email or not password or not confirm_password:
            messages.error(request, "All fields are required")
            return redirect("signup")

        # Password match check
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        # Email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered")
            return redirect("signup")

        # Username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect("signup")

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Account created successfully! Please login.")
        return redirect("login")

    return render(request, "signup.html")


from django.core.mail import send_mail


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid Username or Password")
            return redirect('login')   # 👈 THIS IS IMPORTANT
    
    return render(request, 'login.html')



from django.contrib import messages

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        try:
            user = User.objects.get(email=email)

            if password == confirm_password:
                user.set_password(password)
                user.save()
                messages.success(request, "Password changed successfully!")
                return redirect("login")
            else:
                messages.error(request, "Passwords do not match!")

        except User.DoesNotExist:
            messages.error(request, "Email not registered!")

    return render(request, "forgot_password.html")


def forgot_username(request):
    username = None

    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            messages.error(request, "Email not registered!")

    return render(request, "forgot_username.html", {"username": username})

# Logout
def logout_view(request):
    logout(request)
    return redirect('login')

# Dashboard
def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'dashboard.html')


@login_required
def generate_bill(request):
    shop, created = ShopProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":

        # -----------------------------
        # Customer Details
        # -----------------------------
        customer_name = request.POST.get("customer_name")
        customer_phone = request.POST.get("customer_phone")
        payment_method = request.POST.get("payment_method")
        action = request.POST.get("action")

        # -----------------------------
        # Product Details
        # -----------------------------
        product_names = request.POST.getlist("product_name[]")
        quantities = request.POST.getlist("quantity[]")
        prices = request.POST.getlist("price[]")

        # -----------------------------
        # Generate Invoice Number
        # -----------------------------
        today_str = datetime.datetime.now().strftime("%Y%m%d")
        invoice_no = f"INV-{today_str}-{uuid.uuid4().hex[:6].upper()}"

        # -----------------------------
        # Calculate Total
        # -----------------------------
        total = 0
        for i in range(len(product_names)):
            qty = int(quantities[i])
            price = float(prices[i])
            total += qty * price

        # Tax Calculation (9% + 9%)
        cgst = round(total * 0.09, 2)
        sgst = round(total * 0.09, 2)
        grand_total = round(total + cgst + sgst, 2)

        # -----------------------------
        # Create Bill (AFTER calculation)
        # -----------------------------
        bill = Bill.objects.create(
            user=request.user,
            invoice_no=invoice_no,
            customer_name=customer_name,
            customer_phone=customer_phone,
            total_amount=total,
            cgst=cgst,
            sgst=sgst,
            grand_total=grand_total,
            payment_method=payment_method,
        )

        # -----------------------------
        # Save Bill Items
        # -----------------------------
        for i in range(len(product_names)):
            BillItem.objects.create(
                bill=bill,
                product_name=product_names[i],
                qty=int(quantities[i]),
                rate=float(prices[i])
            )

        # -----------------------------
        # Generate QR if Online Payment
        # -----------------------------
        
        # -----------------------------
        # Redirect
        # -----------------------------
        
        return redirect("generate_invoice", bill_id=bill.id)

    return render(request, "generate_bill.html", {"shop": shop})

def view_bill(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)

    if request.method == "POST":
        if request.POST.get("action") == "save":
            bill.is_saved = True   # optional field
            bill.save()
            return redirect("bills_history")

    return render(request, "view_bill.html", {
        "bill": bill,
        "shop": bill.user.shopprofile
    })


@login_required
def bills_history(request):
    bills = Bill.objects.filter(
        user=request.user,
        is_deleted=False
    ).order_by('-created_at')

    return render(request, "bills_history.html", {"bills": bills})


@login_required
def shop_profile_view(request):
    shop = request.user.shopprofile
   
    if request.method == "POST":
        # Save in DB
        shop.shop_name = request.POST.get("shop_name", "").strip()
        shop.address = request.POST.get("address", "").strip()
        shop.phone = request.POST.get("phone", "").strip()
        shop.gstin = request.POST.get("gstin", "").strip()
        shop.upi_id = request.POST.get("upi_id", "").strip()
        shop.save()
    return render(request, "ShopProfile.html", {"shop": shop})
                           
@login_required
def trash_bill(request, bill_id):
    bill = Bill.objects.get(id=bill_id, user=request.user)
    bill.is_deleted = True
    bill.save()
    return redirect("bill_history")

@login_required
def trash_list(request):
    bills = Bill.objects.filter(user=request.user, is_deleted=True)
    return render(request, "trash.html", {"bills": bills})

@login_required
def restore_bill(request, bill_id):
    bill = Bill.objects.get(id=bill_id, user=request.user)
    bill.is_deleted = False
    bill.save()
    return redirect("trash")

@login_required
def delete_bill(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id, user=request.user)
    bill.is_deleted = True
    bill.save()
    return redirect("bills_history")




@login_required
def generate_invoice(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id, user=request.user)
    shop = request.user.shopprofile  # your shop info

    qr_base64 = None
    if bill.payment_method.lower() == "online" and shop.upi_id:
        upi_url = f"upi://pay?pa={shop.upi_id}&pn={shop.shop_name}&am={bill.grand_total}&cu=INR"
        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(upi_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    items = BillItem.objects.filter(bill=bill)

    context = {
        "bill": bill,
        "shop": shop,
        "items": items,
        "qr_code": qr_base64,  # send QR code to template
    }
    return render(request, "view_bill.html", context)