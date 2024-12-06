from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, TemplateView, ListView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib.auth.mixins import UserPassesTestMixin
from users.models import RoleRequest, User
from users.forms import CustomUserCreationForm, RoleRequestForm, UserProfileForm


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


class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    View for listing users.
    """

    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"
    paginate_by = 10
    ordering = ["username"]

    def test_func(self):
        """
        method to check if the user is an admin or manager.
        """
        return (
            self.request.user.is_superuser
            or self.request.user.is_manager
        )

    def get_queryset(self):
        """
        method to get the queryset of users.
        """
        queryset = super().get_queryset().select_related('status')
        query = self.request.GET.get("q")
        ordering = self.request.GET.get("ordering", "username")

        if query:
            queryset = queryset.filter(
                Q(username__icontains=query)
                | Q(email__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
            )

        if ordering in [
            "username",
            "-username",
            "email",
            "-email",
            "first_name",
            "-first_name",
            "last_name",
            "-last_name",
        ]:
            queryset = queryset.order_by(ordering)

        return queryset



class UserDetailView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    View for displaying user details.
    """

    template_name = "users/user_detail.html"

    def test_func(self):
        """
        Проверяет, имеет ли пользователь права на просмотр.
        """
        return (
            self.request.user.is_staff
            or self.request.user.is_manager
            or self.request.user.pk == self.kwargs.get("pk")
        )

    def get_context_data(self, **kwargs):
        """
        Добавляет в контекст информацию о пользователе.
        """
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get("pk")  


        try:
            user = User.objects.select_related("status").get(pk=user_id)
            context["user_detail"] = user
            context["is_online"] = getattr(user.status, "is_online", False)
        except User.DoesNotExist:
            context["user_detail"] = None
            context["is_online"] = False

        return context

    


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/edit_profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user