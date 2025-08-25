from django.urls import path
from emp import views
from django.contrib.auth import views as auth_views
from emp.views import CustomPasswordResetView

urlpatterns = [
    path("home/", views.emp_home, name="emp_home"),
    path("add-emp/", views.add_emp, name="add_emp"),
    path("view-emp/", views.view_emp, name="view_emp"), 
    path("update-emp/", views.update_emp, name="update_emp"),
    path("delete-emp/<int:emp_id>/", views.delete_emp, name="delete_emp"),

    path("register/", views.register_user, name="register"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),

    # ✅ Password reset flow
    path('reset-password/', CustomPasswordResetView.as_view(), name='password_reset'),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="emp/password_reset_done.html"), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="emp/password_reset_confirm.html"), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(template_name="emp/password_reset_complete.html"), name="password_reset_complete"),

    # ✅ Support tickets
    path("help_support/", views.help_support, name="help_support"),
    path("guest-help-support/", views.guest_help_support, name="guest_help_support"),
]

