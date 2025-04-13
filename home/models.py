from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.urls import reverse


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class OTP(models.Model):
    email = models.EmailField(null=True, blank=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP for {self.email or 'unknown'}"


class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('customer_detail', kwargs={'pk': self.pk})


class CustomerPlan(models.Model):
    PLAN_DURATION_CHOICES = [
        ('1_month', '1 Month'),
        ('3_months', '3 Months'),
        ('6_months', '6 Months'),
        ('1_year', '1 Year'),
        ('3_years', '3 Years'),
    ]
    
    PLAN_NAME_CHOICES = [
        ('Basic', 'Basic'),
        ('Standard', 'Standard'),
        ('Premium', 'Premium'),
        ('Custom', 'Custom'),
    ]
    
    SERVICE_NAME_CHOICES = [
        ('Web Development', 'Web Development'),
        ('Mobile App Development', 'Mobile App Development'),
        ('SEO Services', 'SEO Services'),
        ('Digital Marketing', 'Digital Marketing'),
        ('Graphic Design', 'Graphic Design'),
        ('Custom', 'Custom'),
    ]

    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='plans')
    service_name = models.CharField(max_length=50, choices=SERVICE_NAME_CHOICES, default='Web Development')
    plan_name = models.CharField(max_length=20, choices=PLAN_NAME_CHOICES)
    plan_duration = models.CharField(max_length=20, choices=PLAN_DURATION_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    service_details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    plan_id = models.CharField(max_length=20, unique=True, blank=True)

    def __str__(self):
        return f"{self.customer.name} - {self.service_name} ({self.plan_name})"

    def get_absolute_url(self):
        return reverse('customer_plan_detail', kwargs={'pk': self.pk})

    @property
    def discounted_price(self):
        return self.price * (1 - self.discount/100)

    def save(self, *args, **kwargs):
        if not self.plan_id:
            self.plan_id = f"PLAN-{self.customer.pk}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        super().save(*args, **kwargs)


class CompletedWork(models.Model):
    project_name = models.CharField(max_length=200)
    customer_name = models.CharField(max_length=200)
    description = models.TextField()
    days_taken = models.IntegerField()
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.project_name
    

class OngoingWork(models.Model):
    project_name = models.CharField(max_length=200)
    customer_name = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    advance_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    def __str__(self):
        return self.project_name
    

class Payment(models.Model):
    project_name = models.CharField(max_length=200)
    customer_name = models.CharField(max_length=200)
    payment_type = models.CharField(max_length=50, choices=[('Advance', 'Advance'), ('Clearance', 'Clearance')])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.project_name} - {self.payment_type} - RS {self.amount}"