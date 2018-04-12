try:
    from autoslug import AutoSlugField
except ImportError:
    from django import urls
    import sys

    # Restore old Django API if Autoslugfield import fail for Django 2.0 and
    # older versions of the package.
    sys.modules['django.core.urlresolvers'] = urls
    from autoslug import AutoSlugField