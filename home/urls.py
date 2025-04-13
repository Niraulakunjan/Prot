# home/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    # for dashboard
    path('customer/', views.customer_view, name='customer'),
     path('add-customer/', views.add_customer_view, name='add_customer'),
    path('completed-work/', views.completed_work_view, name='completed_work'),
     path('ongoing-work/', views.ongoing_work_view, name='ongoing_work'),
    path('add-ongoing-work/', views.add_ongoing_work_view, name='add_ongoing_work'),
    path('mark-as-complete/', views.mark_as_complete_view, name='mark_as_complete'),
    path('ongoing-work/', views.ongoing_work_view, name='ongoing_work'),
    path('completed-work/', views.completed_work_view, name='completed_work'),
    path('add-ongoing-work/', views.add_ongoing_work_view, name='add_ongoing_work'),
    path('mark-as-complete/', views.mark_as_complete_view, name='mark_as_complete'),  
    path('payment-history/', views.payment_history_view, name='payment_history'),
    path('send-email/', views.send_email_view, name='send_email'),
    path('send-invoice-email/', views.send_invoice_email_view, name='send_invoice_email'),
    path('send-about-myself-email/', views.send_about_myself_email_view, name='send_about_myself_email'),
    path('services/', views.services_view, name='services'),
    path('add-service/', views.add_service_view, name='add_service'),
    path('delete-service/<int:service_id>/', views.delete_service_view, name='delete_service'),
    path('edit-service/<int:service_id>/', views.edit_service_view, name='edit_service'),
    path('services/', views.services_view, name='services'),
    path('add-service/', views.add_service_view, name='add_service'),
     path('services/', views.services_view, name='services'),
    path('add-customer-plan/', views.add_customer_plan_view, name='add_customer_plan'),
    path('edit-customer-plan/<int:customer_id>/', views.edit_customer_plan, name='edit_customer_plan'),
    path('delete-customer-plan/<int:plan_id>/', views.delete_customer_plan, name='delete_customer_plan'),
    path('delete-service/<int:service_id>/', views.delete_service_view, name='delete_service'),
    path('edit-service/<int:service_id>/', views.edit_service_view, name='edit_service'),
    path('edit-customer/<int:customer_id>/', views.edit_customer_view, name='edit_customer'),
    path('send-renewal-email/', views.send_renewal_email, name='send_renewal_email'),
    path('database/', views.database_overview, name='database_overview'),
]