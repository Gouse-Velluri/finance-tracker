"""
Context processors to inject global template variables.
"""
from .models import UserProfile


def theme_context(request):
    """Inject dark_mode and currency into every template."""
    dark_mode = False
    currency = '$'

    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            dark_mode = profile.dark_mode
            currency = profile.currency
        except UserProfile.DoesNotExist:
            pass

    return {
        'dark_mode': dark_mode,
        'user_currency': currency,
    }
