import time

# Generated once at server start — changes on every restart/deploy
_CACHE_VERSION = str(int(time.time()))


def cache_version(request):
    return {'CACHE_VERSION': _CACHE_VERSION}
