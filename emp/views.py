from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy

from .models import Emp, Profile, SupportTicket, GuestSupportTicket
from .forms import CustomPasswordResetForm, SupportTicketForm, GuestSupportTicketForm
import re




# ================== EMPLOYEE VIEWS ==================


def emp_home(request):
    emp = None
    email_name = "Guest"

    if request.user.is_authenticated:
        # fetch employee linked to this user if exists
        emp = Emp.objects.filter(user=request.user).first()

        # Always take from login email (User model)
        if request.user.email:
            raw_email_name = request.user.email.split("@")[0]
        else:
            raw_email_name = request.user.username

        # Remove digits, keep only letters
        email_name = re.sub(r'[^a-zA-Z]', '', raw_email_name)

    total_emps = Emp.objects.count()

    return render(request, 'emp/home.html', {
        'emp': emp,
        'total_emps': total_emps,
        'email_name': email_name
    })


@login_required(login_url='/emp/login/')
def add_emp(request):
    # Block if this user already has details
    if Emp.objects.filter(user=request.user).exists():
        messages.warning(request, "You have already added your details. You can edit or delete them instead.")
        return redirect('/emp/view-emp/')

    if request.method == 'POST':
        # Generate emp_code safely
        last_emp = Emp.objects.exclude(emp_code__isnull=True).order_by('-emp_code').first()
        if last_emp and last_emp.emp_code:
            try:
                last_num = int(last_emp.emp_code.replace("EMP", ""))
            except ValueError:
                last_num = 0
        else:
            last_num = 0

        new_code = f"EMP{last_num + 1:03d}"

        # Collect form data
        f_name = request.POST.get('f_name')
        l_name = request.POST.get('l_name')
        gender = request.POST.get('gender')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        department = request.POST.get('department')
        designation = request.POST.get('designation')
        joining_date = request.POST.get('joining_date')

        # Validate required fields
        if not all([f_name, l_name, gender, phone, email, address, department, designation, joining_date]):
            messages.warning(request, "Please fill all required fields.")
            return redirect('/emp/add-emp/')

        # Extra safety check again (in case of race condition)
        if Emp.objects.filter(user=request.user).exists():
            messages.warning(request, "Your details are already saved.")
            return redirect('/emp/view-emp/')

        # Create Employee
        Emp.objects.create(
            user=request.user,
            emp_code=new_code,
            f_name=f_name,
            l_name=l_name,
            gender=gender,
            phone=phone,
            email=email,
            address=address,
            department=department,
            designation=designation,
            joining_date=joining_date
        )

        messages.success(request, "Employee added successfully.")
        return redirect('/emp/view-emp/')

    return render(request, 'emp/add_emp.html')



@login_required(login_url='/emp/login/')
def view_emp(request):
    emps = Emp.objects.all()  # Show all employees to everyone
    return render(request, 'emp/view_emp.html', {'emps': emps})


@login_required(login_url='/emp/login/')
def update_emp(request):
    try:
        # ✅ Only fetch logged-in user's own details
        emp = Emp.objects.get(user=request.user)
    except Emp.DoesNotExist:
        messages.warning(request, "You have not added your employee details yet.")
        return redirect("/emp/view-emp/")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "delete":
            emp.delete()
            messages.success(request, "Your employee record was deleted successfully.")
            return redirect("/emp/view-emp/")

        elif action == "update":
            emp.phone = request.POST.get("phone")
            emp.email = request.POST.get("email")
            emp.address = request.POST.get("address")
            emp.department = request.POST.get("department")
            emp.designation = request.POST.get("designation")

            # ✅ Prevent duplicate email for other employees
            if Emp.objects.exclude(pk=emp.pk).filter(email=emp.email).exists():
                messages.error(request, "Email already exists. Please use a different one.")
                return redirect("/emp/update-emp/")

            emp.save()
            messages.success(request, "Your details have been updated successfully.")
            return redirect("/emp/view-emp/")

    return render(request, "emp/update_emp.html", {"emp": emp})



def delete_emp(request, emp_id):
    emp = get_object_or_404(Emp, pk=emp_id, user=request.user)  # ✅ Only delete if it's their own record
    emp.delete()
    messages.success(request, "Employee deleted successfully.")
    return redirect("/emp/view-emp/")










# ================== AUTH VIEWS ==================

def register_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # ✅ Check password match
        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('/emp/register/')

        # ✅ Check if email already exists
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered")
            return redirect('/emp/register/')

        # ✅ Validate password with Django’s built-in + custom validators
        try:
            validate_password(password1)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return redirect('/emp/register/')

        # ✅ Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password1,
            is_active=True  # User is active, approval is handled via Profile
        )

        # ✅ Ensure Profile is created
        profile, created = Profile.objects.get_or_create(user=user)
        if not created:
            profile.is_approved = False
            profile.save()

        messages.success(request, "Registered successfully. Please wait for admin approval.")
        return redirect('/emp/login/')

    return render(request, 'emp/register.html')



def login_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            try:
                profile = Profile.objects.get(user=user)
            except Profile.DoesNotExist:
                messages.error(request, "No profile found. Contact admin.")
                return redirect('/emp/login/')

            # Strict check: block if not approved
            if not profile.is_approved:
                messages.error(request, "Your account is not approved yet. Please wait for admin approval.")
                return redirect('/emp/login/')

            # If approved, allow login
            login(request, user)
            return redirect('/emp/home/')
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'emp/login.html')



class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = "emp/password_reset.html"
    email_template_name = "emp/password_reset_email.html"
    success_url = reverse_lazy('password_reset_done')



def logout_user(request):
    logout(request)
    return redirect('/emp/login/')


def help_support(request):
    if request.method == "POST":
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user  # always logged-in user
            ticket.save()
            messages.success(request, "✅ Your support request has been submitted!")
            return redirect("help_support")
    else:
        form = SupportTicketForm()

    tickets = SupportTicket.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "emp/help_support.html", {"form": form, "tickets": tickets})


def guest_help_support(request):
    if request.method == "POST":
        form = GuestSupportTicketForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Your support request has been submitted!")
            return redirect("guest_help_support")
    else:
        form = GuestSupportTicketForm()

    return render(request, "emp/guest_help_support.html", {"form": form})
    
