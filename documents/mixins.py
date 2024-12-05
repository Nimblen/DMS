from django.core.exceptions import PermissionDenied

class RoleRequiredMixin:
    """
    A mixin for views that checks if the user has the required role.
    """
    required_role = None

    def dispatch(self, request, *args, **kwargs):
        """
        Checks if the user has the required role. If not, raises PermissionDenied.
        """
        if self.required_role and not getattr(request.user, f'is_{self.required_role}')():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
