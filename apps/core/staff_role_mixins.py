from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseForbidden


class RoleRequiredMixin:
    """
    allowed_roles: tupla de valores User.Role (ej. ("admin", "tactical_analyst")).
    Si está vacía, solo exige usuario autenticado.
    """

    allowed_roles: tuple[str, ...] = ()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), login_url="/accounts/login/")

        if self.allowed_roles and getattr(request.user, "role", None) not in self.allowed_roles:
            return HttpResponseForbidden("No tienes permiso para ver esta sección.")

        return super().dispatch(request, *args, **kwargs)