from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.apps import apps
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from datetime import date
from django.db.models import Q
# from trash_collector.accounts.forms import CustomUserForm

# from trash_collector.customers.models import Customer

from .models import Employee

# Create your views here.

# TODO: Create a function for each path created in employees/urls.py. Each will need a template as well.

@login_required
def index(request):
    # The following line will get the logged-in user (if there is one) within any view function
    logged_in_user = request.user
    try:
        # This line will return the customer record of the logged-in user if one exists
        logged_in_employee = Employee.objects.get(user=logged_in_user)
        today = date.today()
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        Customer = apps.get_model('customers.Customer')
        all_customers = Customer.objects.all()
        customers_in_zipcode =  all_customers.filter(zip_code = logged_in_employee.zipcode)
        customers_pickup_day = customers_in_zipcode.filter(Q(weekly_pickup = days[date.weekday(today)]) | Q(one_time_pickup = today))
        customers_not_suspended = customers_pickup_day.exclude(Q(suspend_start__lt=today) & Q(suspend_end__gt=today))
        customers_need_pickup = customers_not_suspended.exclude(date_of_last_pickup = today)
        context = {
            'logged_in_employee': logged_in_employee,
            'today': today,
            'customers_need_pickup' : customers_need_pickup
        }
        return render(request, 'employees/index.html', context)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('employees:create'))

    

@login_required
def create(request):
    logged_in_user = request.user
    if request.method == "POST":
        name_from_form = request.POST.get('name')
        address_from_form = request.POST.get('address')
        zip_from_form = request.POST.get('zip_code')
        new_employee = Employee(name=name_from_form, user=logged_in_user,
                                address=address_from_form, zipcode=zip_from_form)
        new_employee.save()
        return HttpResponseRedirect(reverse('employees:index'))
    else:
        return render(request, 'employees/create.html')


@login_required
def edit_profile(request):
    logged_in_user = request.user
    logged_in_employee = Employee.objects.get(user=logged_in_user)
    if request.method == "POST":
        name_from_form = request.POST.get('name')
        address_from_form = request.POST.get('address')
        zip_from_form = request.POST.get('zipcode')
        logged_in_employee.name = name_from_form
        logged_in_employee.address = address_from_form
        logged_in_employee.zipcode = zip_from_form
        logged_in_employee.save()
        return HttpResponseRedirect(reverse('employees:index'))
    else:
        context = {
            'logged_in_employee': logged_in_employee
        }
        return render(request, 'employees/edit_profile.html', context)

@login_required
def confirm_pickup(request, customer_id):
    Customer = apps.get_model('customers.Customer')
    customers_update = Customer.objects.get(id = customer_id)
    customers_update.date_of_last_pickup = date.today()
    customers_update.balance += 20
    customers_update.save()
    
    return HttpResponseRedirect(reverse('employees:index'))

@login_required
def weekday_pickup_search(request):
    Customer = apps.get_model('customers.Customer')
    logged_in_user = request.user

    logged_in_employee = Employee.objects.get(user=logged_in_user)
    employee_zip_code = logged_in_employee.zipcode

    if request.method == "POST":
        weekday_from_form = request.POST.get('days')

        customer_match = Customer.objects.filter(zip_code=employee_zip_code)\
            .filter(weekly_pickup=weekday_from_form)\

        selected_day = weekday_from_form

        context = {
            'customer_match': customer_match,
            'logged_in_employee': logged_in_employee,
            'selected_day': selected_day,
        }

        return render(request, 'employees/weekday_pickup_search.html', context)
    else:
        today = date.today()

        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        today_weekday = days[today.weekday()]

        customer_match = Customer.objects.filter(zip_code=employee_zip_code)\
            .filter(weekly_pickup=today_weekday)

        selected_day = today_weekday

        context = {
            'customer_match': customer_match,
            'logged_in_employee': logged_in_employee,
            'selected_day': selected_day
        }
        return render(request, 'employees/weekday_pickup_search.html', context)