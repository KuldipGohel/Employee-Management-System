from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from .models import SupportTicket, GuestSupportTicket


class CustomPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is not registered. Please register first.")
        return email



class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ["subject", "message"]


class GuestSupportTicketForm(forms.ModelForm):
    class Meta:
        model = GuestSupportTicket
        fields = ["email", "subject", "message"]

