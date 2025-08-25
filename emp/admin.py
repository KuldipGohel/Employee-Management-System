from django.contrib import admin
from .models import Profile, Emp, SupportTicket, GuestSupportTicket


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_approved')
    list_editable = ('is_approved',)


@admin.register(Emp)
class EmpAdmin(admin.ModelAdmin):
    list_display = ('emp_id', 'f_name', 'l_name', 'email', 'department', 'designation')
    search_fields = ('f_name', 'l_name', 'email', 'department', 'designation')
    list_filter = ('department', 'designation')


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ("subject", "user", "created_at", "is_resolved")
    list_editable = ("is_resolved",)
    list_filter = ("is_resolved", "created_at")
    search_fields = ("subject", "message", "user__username", "user__email")


@admin.register(GuestSupportTicket)
class GuestSupportTicketAdmin(admin.ModelAdmin):
    list_display = ("subject", "email", "created_at", "is_resolved")
    list_editable = ("is_resolved",)
    list_filter = ("is_resolved", "created_at")
    search_fields = ("subject", "message", "email")
