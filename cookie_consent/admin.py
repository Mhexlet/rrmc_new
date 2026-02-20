from django.contrib import admin
from .models import CookieConsentSettings


@admin.register(CookieConsentSettings)
class CookieConsentSettingsAdmin(admin.ModelAdmin):
    """Админка для настроек cookie-баннера (singleton)."""

    list_display = ('__str__', 'hide_days', 'policy_url')

    def has_add_permission(self, request):
        # Разрешаем создание только если записи ещё нет
        return not CookieConsentSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
