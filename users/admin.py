from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import RoleRequest, User


class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "role", "is_staff")
    list_filter = ("role", "is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Персональная информация", {"fields": ("first_name", "last_name", "email")}),
        (
            "Роли и разрешения",
            {
                "fields": (
                    "role",
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "role",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )


admin.site.register(User, CustomUserAdmin)


@admin.register(RoleRequest)
class RoleRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "requested_role", "is_approved", "created_at")
    list_filter = ("requested_role", "is_approved")
    actions = ["approve_requests", "reject_requests"]

    def approve_requests(self, request, queryset):
        for role_request in queryset:
            role_request.user.role = role_request.requested_role
            role_request.user.save()
            role_request.is_approved = True
            role_request.save()

    approve_requests.short_description = "Одобрить выбранные запросы"

    def reject_requests(self, request, queryset):
        queryset.update(is_approved=False)

    reject_requests.short_description = "Отклонить выбранные запросы"
