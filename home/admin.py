from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.contrib import admin
from .models import User, OTP, Customer, CustomerPlan, CompletedWork, OngoingWork, Payment
User = get_user_model()
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp', 'created_at', 'is_verified')
    search_fields = ('email',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email')

@admin.register(CustomerPlan)
class CustomerPlanAdmin(admin.ModelAdmin):
    list_display = ('customer', 'service_name', 'plan_name', 'start_date', 'end_date', 'price')
    list_filter = ('service_name', 'plan_name', 'plan_duration')
    search_fields = ('customer__name', 'service_name', 'plan_name')

@admin.register(CompletedWork)
class CompletedWorkAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'customer_name', 'date', 'amount')
    search_fields = ('project_name', 'customer_name')

@admin.register(OngoingWork)
class OngoingWorkAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'customer_name', 'start_date', 'amount')
    search_fields = ('project_name', 'customer_name')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'customer_name', 'payment_type', 'amount', 'date')
    list_filter = ('payment_type',)
    search_fields = ('project_name', 'customer_name')