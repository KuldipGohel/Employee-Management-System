from django.db import models
from django.contrib.auth.models import User



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)


    def __str__(self):
        return self.user.username
    


class Emp(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)  # <--- Only one Emp per user
    emp_id = models.AutoField(primary_key=True)
    emp_code = models.CharField(max_length=10, unique=True, editable=False, null=True, blank=True) # Format: EMP001, EMP002, etc.
    f_name = models.CharField(max_length=100)
    l_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(max_length=50, unique=True)
    address = models.CharField(max_length=100)
    department = models.CharField(max_length=50)
    designation = models.CharField(max_length=50)
    joining_date = models.DateField()

    
    def save(self, *args, **kwargs):
        if not self.emp_code:  # Generate only when creating
            last_emp = Emp.objects.exclude(emp_code__isnull=True).order_by('-emp_id').first()
            if last_emp and last_emp.emp_code:
                try:
                    last_num = int(last_emp.emp_code.replace("EMP", ""))
                except ValueError:
                    last_num = 0
                new_num = last_num + 1
            else:
                new_num = 1
            self.emp_code = f"EMP{new_num:03d}"  # Format → EMP001, EMP002
        super(Emp, self).save(*args, **kwargs)


    def __str__(self):
        return f"{self.f_name} {self.l_name}"



class SupportTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Always required now
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} - {self.user.email}"


class GuestSupportTicket(models.Model):
    email = models.EmailField()  
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} - {self.email}"
