from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from users.models import RoleRequest
from users.forms import CustomUserCreationForm, RoleRequestForm


class UserRegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")


class UserLoginView(LoginView):
    template_name = "users/login.html"


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("index")


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = "users/profile.html"


class RoleRequestCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a role request.

    This view handles the creation of a role request by the user.
    It requires the user to be logged in and checks for any existing
    pending requests before allowing a new one to be created.
    """

    model = RoleRequest
    form_class = RoleRequestForm
    template_name = "users/role_request_form.html"
    success_url = reverse_lazy("users:role_request_success")

    def get_form_kwargs(self):
        """
        Add the current user to the form kwargs.

        Returns:
            dict: The keyword arguments for initializing the form.
        """
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        """
        Validate the form and handle role request creation.

        Checks if there is an existing pending role request for the user.
        If there is, displays a warning message and prevents the form from
        being submitted. Otherwise, assigns the current user to the role
        request and submits the form.

        Args:
            form (Form): The submitted form.

        Returns:
            HttpResponse: The response object.
        """
        # Check for existing pending role request
        existing_request = RoleRequest.objects.filter(
            user=self.request.user, is_approved__isnull=True
        ).first()
        if existing_request:
            # Warn the user about the existing pending request
            messages.warning(
                self.request,
                "Вы уже отправили запрос на изменение роли, который ожидает рассмотрения.",
            )
            return self.form_invalid(form)

        # Assign the current user to the role request
        form.instance.user = self.request.user
        messages.success(self.request, "Ваш запрос на изменение роли отправлен.")
        return super().form_valid(form)
