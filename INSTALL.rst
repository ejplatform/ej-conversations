=========================
Installation instructions
=========================

``ej-conversations`` can be installed using pip::

    $ pip3 install ej-conversations

This command will fetch the archive and its dependencies from the internet and
install them. This app only works for Python 3.6+ and requires Django 1.11+.

In Django, you must add it to the INSTALLED_APPS list in settings.py::


    INSTALLED_APPS = [
        'ej_conversations',

        # other apps...
    ]
