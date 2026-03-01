from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='home'),
    path('login/', views.login_view, name='login'),

    # ✅ Custom Forgot Password (No Email, Direct Reset)
    path('forgot-password/', views.forgot_password, name='forgot_password'),

    path('forgot-username/', views.forgot_username, name='forgot_username'),

    path('signup/', views.signup_view, name='signup'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),

    path("shop/", views.shop_profile_view, name="shop_profile"),
    path("generate/", views.generate_bill, name="generate_bill"),
    
    path("view/<int:bill_id>/", views.view_bill, name="view_bill"),

    path('trash/', views.trash_list, name='trash'),
    path('trash/<int:bill_id>/', views.trash_bill, name='trash_bill'),
    path('restore/<int:bill_id>/', views.restore_bill, name='restore_bill'),

    path("bills-history/", views.bills_history, name="bills_history"),
    path("delete-bill/<int:bill_id>/", views.delete_bill, name="delete_bill"),
    path('invoice/<int:bill_id>/', views.generate_invoice, name='generate_invoice'),
]