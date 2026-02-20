from .models import CookieConsentSettings


def cookie_consent(request):
    """Передаёт настройки cookie-баннера во все шаблоны."""
    settings = CookieConsentSettings.load()
    return {
        'cookie_consent_message': settings.message,
        'cookie_consent_policy_url': settings.policy_url,
        'cookie_consent_hide_days': settings.hide_days,
    }
