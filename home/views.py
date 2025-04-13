# home/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import User, OTP
import random
from django.core.mail import send_mail
from django.conf import settings
from .models import Customer 
from .models import CompletedWork
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import OngoingWork, Payment , Customer ,CustomerPlan

def home(request):
    return render(request, 'home/home.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password')
    return render(request, 'home/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


def register_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'home/register.html')
        
        # Store user data in session
        request.session['registration_data'] = {
            'email': email,
            'password': password,
            'first_name': first_name,
            'last_name': last_name
        }
        
        # Generate and store OTP
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        OTP.objects.create(email=email, otp=otp)
        
        # Send OTP email
        subject = 'Verify Your Email - Portfolio'
        message = f'Your OTP for email verification is: {otp}'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        
        try:
            send_mail(
                subject,
                message,
                from_email,
                recipient_list,
                fail_silently=False
            )
            messages.success(request, 'OTP sent to your email')
            return redirect('verify_otp')
        except Exception as e:
            messages.error(request, f'Error sending OTP: {str(e)}')
            # Clear session if email fails
            request.session.pop('registration_data', None)
            return render(request, 'home/register.html')
    
    return render(request, 'home/register.html')


def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST['otp']
        try:
            otp_obj = OTP.objects.filter(otp=otp, is_verified=False).latest('created_at')
            registration_data = request.session.get('registration_data')
            
            if not registration_data:
                messages.error(request, 'Session expired. Please register again.')
                return redirect('register')
            
            if otp_obj.email != registration_data['email']:
                messages.error(request, 'Invalid OTP or email mismatch')
                return render(request, 'home/verify_otp.html')
            
            # OTP is valid, create user
            user = User.objects.create_user(
                email=registration_data['email'],
                password=registration_data['password'],
                first_name=registration_data['first_name'],
                last_name=registration_data['last_name'],
                is_active=True
            )
            
            # Mark OTP as verified
            otp_obj.is_verified = True
            otp_obj.save()
            
            # Log the user in
            login(request, user)
            
            # Clear session data
            request.session.pop('registration_data', None)
            
            messages.success(request, 'Registration successful!')
            return redirect('home')
        
        except OTP.DoesNotExist:
            messages.error(request, 'Invalid OTP')
    
    return render(request, 'home/verify_otp.html')


# for dashboard 

def dashboard_view(request):
    if request.user.is_authenticated:
       return render(request, 'home/dashboard.html')
    else:
        messages.error(request, 'You need to log in first.')
        return redirect('login')

 # Assuming you have a Customer model

@login_required
def customer_view(request):
    query = request.GET.get('q', '')  # Get the search query
    if query:
        customers = Customer.objects.filter(name__icontains=query)  # Filter customers by name
    else:
        customers = Customer.objects.all()  # Show all customers
    return render(request, 'home/customer.html', {'customers': customers})

@login_required
def add_customer_view(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        created_at = request.POST['date_added']
        Customer.objects.create(name=name, email=email, created_at=created_at)
        return redirect('customer')  # Redirect back to the customer list
    return render(request, 'home/customer.html')

@login_required
def completed_work_view(request):
    query = request.GET.get('q', '')  # Get the search query
    if query:
        completed_works = CompletedWork.objects.filter(project_name__icontains=query)  # Filter by project name
    else:
        completed_works = CompletedWork.objects.all()  # Show all completed work
    return render(request, 'home/completed_work.html', {'completed_works': completed_works})

def ongoing_work_view(request):
    return render(request, 'home/ongoing_work.html')

# Assuming you have a CompletedWork model
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import OngoingWork, CompletedWork

@login_required
def ongoing_work_view(request):
    query = request.GET.get('q', '')  # Get the search query
    if query:
        ongoing_works = OngoingWork.objects.filter(project_name__icontains=query)  # Filter by project name
    else:
        ongoing_works = OngoingWork.objects.all()  # Show all ongoing work

    # Calculate remaining amount for each work
    for work in ongoing_works:
        work.remaining_amount = work.amount - work.advance_payment

    return render(request, 'home/ongoing_work.html', {'ongoing_works': ongoing_works})

@login_required
def add_ongoing_work_view(request):
    if request.method == 'POST':
        project_name = request.POST['project_name']
        customer_name = request.POST['customer_name']
        description = request.POST['description']
        start_date = request.POST['start_date']
        amount = request.POST['amount']
        advance_payment = request.POST['advance_payment']
        OngoingWork.objects.create(
            project_name=project_name,
            customer_name=customer_name,
            description=description,
            start_date=start_date,
            amount=amount,
            advance_payment=advance_payment
        )
        return redirect('ongoing_work')  # Redirect back to the ongoing work list
    return render(request, 'home/ongoing_work.html')

@login_required
def mark_as_complete_view(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        work_id = data.get('id')
        work = OngoingWork.objects.get(id=work_id)

        # Calculate the remaining amount
        remaining_amount = work.amount - work.advance_payment

        # Register the remaining payment
        Payment.objects.create(
            project_name=work.project_name,
            customer_name=work.customer_name,
            payment_type='Clearance',
            amount=remaining_amount
        )

        # Move the work to completed work
        CompletedWork.objects.create(
            project_name=work.project_name,
            customer_name=work.customer_name,
            description=work.description,
            days_taken=(work.start_date - work.start_date).days,  # Placeholder for days taken
            date=work.start_date,
            amount=work.amount
        )
        work.delete()  # Remove from ongoing work
        return JsonResponse({'success': True})

@login_required
def payment_history_view(request):
    query = request.GET.get('q', '')  # Get the search query
    if query:
        payments = Payment.objects.filter(customer_name__icontains=query).order_by('-date')  # Filter by customer name
    else:
        payments = Payment.objects.all().order_by('-date')  # Show all payments
    return render(request, 'home/payment_history.html', {'payments': payments})

@login_required
def add_ongoing_work_view(request):
    if request.method == 'POST':
        project_name = request.POST['project_name']
        customer_name = request.POST['customer_name']
        description = request.POST['description']
        start_date = request.POST['start_date']
        amount = request.POST['amount']
        advance_payment = request.POST['advance_payment']

        # Create the ongoing work
        work = OngoingWork.objects.create(
            project_name=project_name,
            customer_name=customer_name,
            description=description,
            start_date=start_date,
            amount=amount,
            advance_payment=advance_payment
        )

        # Register the advance payment
        Payment.objects.create(
            project_name=project_name,
            customer_name=customer_name,
            payment_type='Advance',
            amount=advance_payment
        )

        return redirect('ongoing_work')  # Redirect back to the ongoing work list
    return render(request, 'home/ongoing_work.html')

from django.shortcuts import render
from .models import Customer, OngoingWork


@login_required
def send_email_view(request):
    customers = Customer.objects.all()
    projects = CustomerPlan.objects.all()  # Assuming projects are CustomerPlan; adjust if different
    customer_plans = CustomerPlan.objects.all()  # Add customer_plans
    return render(request, 'home/send_email.html', {
        'customers': customers,
        'projects': projects,
        'customer_plans': customer_plans,
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Customer, OngoingWork

@login_required
def send_invoice_email_view(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        project_id = request.POST.get('project_id')

        # Fetch customer and project details
        customer = get_object_or_404(Customer, id=customer_id)
        project = get_object_or_404(OngoingWork, id=project_id)

        # Calculate the remaining amount
        remaining_amount = project.amount - project.advance_payment

        # Render the email content using an HTML template
        email_subject = f"Invoice for Project: {project.project_name}"
        email_body = render_to_string('home/email_templates/invoice_email.html', {
            'customer': customer,
            'project': project,
            'remaining_amount': remaining_amount,  # Pass remaining amount to the template
        })

        # Send the email
        send_mail(
            subject=email_subject,
            message='',  # Leave plain text message empty
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[customer.email],
            html_message=email_body,  # HTML content
        )

        # Redirect back to the send email page with a success message
        return redirect('send_email')

    return redirect('send_email')

@login_required
def send_about_myself_email_view(request):
    if request.method == 'POST':
        recipient_email = request.POST.get('recipient_email')

        # Email content
        subject = "About My Services"
        html_message = render_to_string('home/email_templates/about_myself_email.html', {
            'website_url': 'https://kunjanniraula.com.np',
        })
        plain_message = "Learn more about my services by visiting https://kunjanniraula.com.np."

        # Send email
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            html_message=html_message,
        )

        return redirect('send_email')  # Redirect back to the Send Email page
 
@login_required   
def services_view(request):
    service_choices = [(x[0], x[1]) for x in CustomerPlan.SERVICE_NAME_CHOICES]
    plan_choices = [(x[0], x[1]) for x in CustomerPlan.PLAN_NAME_CHOICES]
    duration_choices = [(x[0], x[1]) for x in CustomerPlan.PLAN_DURATION_CHOICES]
    return render(request, 'home/services.html', {
        'customers': Customer.objects.all(),
        'customer_plans': CustomerPlan.objects.all(),
        'service_choices': service_choices,
        'plan_choices': plan_choices,
        'duration_choices': duration_choices,
    })

@login_required
def add_service_view(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        price = request.POST['price']
        services_view.objects.create(name=name, description=description, price=price)
        return redirect('services')  # Redirect back to the services list
    return render(request, 'home/add_service.html')

@login_required
def delete_service_view(request, service_id):
    service = get_object_or_404(services_view, id=service_id)
    service.delete()
    return redirect('services')  # Redirect back to the services list
def edit_service_view(request, service_id):
    service = get_object_or_404(services_view, id=service_id)
    if request.method == 'POST':
        service.name = request.POST['name']
        service.description = request.POST['description']
        service.price = request.POST['price']
        service.save()
        return redirect('services')  # Redirect back to the services list
    return render(request, 'home/edit_service.html', {'service': service})

@login_required
def services_view(request):
    customers = Customer.objects.all()  # Fetch all customers
    customer_plans = CustomerPlan.objects.all() 

    
    # Fetch all customer plans
    return render(request, 'home/services.html', {
        'customers': customers,
        'customer_plans': customer_plans,
        'plan_choices': CustomerPlan.PLAN_NAME_CHOICES,
        'service_choices': CustomerPlan.SERVICE_NAME_CHOICES,
        'duration_choices': CustomerPlan.PLAN_DURATION_CHOICES,
        'customer_plans': customer_plans,
        'service_codes': CustomerPlan.SERVICE_NAME_CHOICES,
        'plan_codes': CustomerPlan.PLAN_NAME_CHOICES,
        'duration_codes': CustomerPlan.PLAN_DURATION_CHOICES,
    })
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Customer, CustomerPlan
from django.utils import timezone
from decimal import Decimal

@login_required
def add_customer_plan_view(request):
    if request.method == 'POST':
        try:
            customer_id = request.POST.get('customer_name')
            service_name = request.POST.get('service_name')
            plan_name = request.POST.get('plan_name')
            plan_duration = request.POST.get('plan_duration')
            price = request.POST.get('price')
            discount = request.POST.get('discount', 0)
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            service_details = request.POST.get('service_details', '')

            # Basic validation
            if not all([customer_id, service_name, plan_name, plan_duration, price, start_date, end_date]):
                messages.error(request, "All required fields must be filled.")
                return redirect('services')

            customer = Customer.objects.get(id=customer_id)

            # Create the customer plan
            CustomerPlan.objects.create(
                customer=customer,
                service_name=service_name,
                plan_name=plan_name,
                plan_duration=plan_duration,
                price=Decimal(price),
                discount=Decimal(discount),
                start_date=start_date,
                end_date=end_date,
                service_details=service_details,
                # plan_id will be auto-generated in the save() method
            )

            messages.success(request, "Customer plan added successfully!")
        except Customer.DoesNotExist:
            messages.error(request, "Customer not found.")
        except Exception as e:
            messages.error(request, f"Error adding plan: {str(e)}")
        
        return redirect('services')
    
    # If not POST, redirect to services
    return redirect('services')

@login_required
def edit_customer_plan(request, customer_id):
    plan = get_object_or_404(CustomerPlan, id=customer_id)
    
    if request.method == 'POST':
        try:
            customer_id = request.POST.get('customer_name')
            service_name = request.POST.get('service_name')
            plan_name = request.POST.get('plan_name')
            plan_duration = request.POST.get('plan_duration')
            price = request.POST.get('price')
            discount = request.POST.get('discount', 0)
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            service_details = request.POST.get('service_details', '')

            # Validation
            if not all([customer_id, service_name, plan_name, plan_duration, price, start_date, end_date]):
                messages.error(request, "All required fields must be filled.")
                return redirect('services')

            customer = get_object_or_404(Customer, id=customer_id)

            # Update plan
            plan.customer = customer
            plan.service_name = service_name
            plan.plan_name = plan_name
            plan.plan_duration = plan_duration
            plan.price = Decimal(price)
            plan.discount = Decimal(discount)
            plan.start_date = start_date
            plan.end_date = end_date
            plan.service_details = service_details
            plan.save()

            messages.success(request, "Customer plan updated successfully!")
        except Exception as e:
            messages.error(request, f"Error updating plan: {str(e)}")
        
        return redirect('services')
    
    # If not POST, redirect to services
    return redirect('services')

@login_required
def delete_customer_plan(request, plan_id):
    plan = get_object_or_404(CustomerPlan, id=plan_id)
    
    if request.method in ['POST', 'GET']:  # Allowing both POST and GET for deletion
        try:
            plan.delete()
            messages.success(request, "Customer plan deleted successfully!")
        except Exception as e:
            messages.error(request, f"Error deleting plan: {str(e)}")
    
    return redirect('services')

@login_required
def edit_customer_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    
    if request.method == 'POST':
        customer.name = request.POST['name']
        customer.email = request.POST['email']
        customer.save()
        messages.success(request, "Customer updated successfully!")
        return redirect('customer')  # Redirect back to the customer list
    
    return render(request, 'home/edit_customer.html', {'customer': customer})


from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomerPlan
from datetime import datetime, timedelta

@login_required
def send_renewal_email(request):
    if request.method == 'POST':
        plan_id = request.POST.get('plan_id')
        try:
            plan = CustomerPlan.objects.get(id=plan_id)
            customer = plan.customer

            # Check if plan is nearing renewal (optional, e.g., within 30 days)
            today = datetime.today().date()
            threshold = today + timedelta(days=30)
            if plan.end_date > threshold:
                messages.error(request, f"The plan '{plan.plan_name}' for {customer.name} is not due for renewal yet.")
                return redirect('send_email')

            # Construct email content
            subject = f"Renewal Reminder for Your {plan.plan_name} Plan"
            message = f"Dear {customer.name},\n\n"
            message += f"This is a reminder to renew your {plan.plan_name} plan for {plan.service_name}.\n"
            message += f"End Date: {plan.end_date.strftime('%Y-%m-%d')}\n\n"
            message += "Please contact us to renew your plan or visit our website for more details.\n"
            message += "Best regards,\nYour Company Name"

            # Send email
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[customer.email],
                fail_silently=False,
            )

            messages.success(request, f"Renewal reminder sent to {customer.name} for {plan.plan_name}.")
            return redirect('send_email')

        except CustomerPlan.DoesNotExist:
            messages.error(request, "Plan not found.")
            return redirect('send_email')
        except Exception as e:
            messages.error(request, f"Failed to send email: {str(e)}")
            return redirect('send_email')

    return redirect('send_email')

from django.shortcuts import render
from .models import User, OTP, Customer, CustomerPlan, CompletedWork, OngoingWork, Payment
@login_required
def database_overview(request):
    return render(request, 'home/database_overview.html', {
        'users': User.objects.all(),
        'otps': OTP.objects.all(),
        'customers': Customer.objects.all(),
        'customer_plans': CustomerPlan.objects.all(),
        'completed_works': CompletedWork.objects.all(),
        'ongoing_works': OngoingWork.objects.all(),
        'payments': Payment.objects.all(),
    })