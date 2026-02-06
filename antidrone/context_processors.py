from django.conf import settings as django_settings

# Generated once at server start — changes on every restart/deploy
_CACHE_VERSION = str(getattr(django_settings, 'CACHE_BUST', 0))


def cache_version(request):
    return {
        'CACHE_VERSION': _CACHE_VERSION,
        'settings': django_settings,
    }
