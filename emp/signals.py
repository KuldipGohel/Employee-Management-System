from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile, SupportTicket, GuestSupportTicket


# Profile auto-create
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        Profile.objects.get_or_create(user=instance)


# Approval email
@receiver(post_save, sender=Profile)
def send_approval_email(sender, instance, **kwargs):
    if instance.is_approved:
        try:
            send_mail(
                subject='Your Account Has Been Approved',
                message='Hi, your account is approved. You can now login.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.user.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send approval email: {e}")


# Employee tickets
@receiver(post_save, sender=SupportTicket)
def notify_admin_on_ticket_creation(sender, instance, created, **kwargs):
    if created:
        send_mail(
            subject=f"New Emp Complaint Ticket from {instance.user.email}",
            message=f"Employee: {instance.user.get_full_name()} ({instance.user.email})\n"
                    f"Subject: {instance.subject}\n"
                    f"Message: {instance.message}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=True,
        )


@receiver(post_save, sender=SupportTicket)
def notify_employee_on_ticket_resolve(sender, instance, created, **kwargs):
    if not created and instance.is_resolved:
        send_mail(
            subject="Your Problem is Resolved",
            message=f"Hello {instance.user.first_name},\n\n"
                    f"Your Problem has been resolved:\n\n"
                    f"Subject: {instance.subject}\n"
                    f"Message: {instance.message}\n\n"
                    "Thank you for reaching out.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.user.email],
            fail_silently=True,
        )


# Guest tickets
@receiver(post_save, sender=GuestSupportTicket)
def notify_admin_on_guest_ticket_creation(sender, instance, created, **kwargs):
    if created:
        send_mail(
            subject=f"New Guest Complaint From {instance.email}",
            message=f"Guest Email: {instance.email}\n"
                    f"Subject: {instance.subject}\n"
                    f"Message: {instance.message}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=True,
        )


@receiver(post_save, sender=GuestSupportTicket)
def notify_guest_on_ticket_resolve(sender, instance, created, **kwargs):
    if not created and instance.is_resolved:
        send_mail(
            subject="Your Problem is Resolved",
            message=f"Hello,\n\nYour problem has been resolved:\n\n"
                    f"Subject: {instance.subject}\n"
                    f"Message: {instance.message}\n\n"
                    "Thank you for reaching out.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            fail_silently=True,
        )
