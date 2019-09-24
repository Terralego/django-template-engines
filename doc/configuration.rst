Configuration
=============

ODT engine
-----------

To activate the *ODT engine*, you must specify the following settings:

::

    INSTALLED_APPS = [
        ...
        'template_engines',
    ]

    ...

    TEMPLATES = [
        ...
        {
            'BACKEND': 'template_engines.backends.odt.OdtEngine',
        },
    ]

DOCX engine
------------

To activate the *DOCX engine*, you must specify the following settings:

::

    INSTALLED_APPS = [
        ...
        'template_engines',
    ]

    ...

    TEMPLATES = [
        ...
        {
            'BACKEND': 'template_engines.backends.docx.DocxEngine',
        },
    ]

Advanced settings
-----------------

Other settings can be specified as:
 * ``DIRS`` a list of directories to search for templates
 * ``APP_DIRS`` a boolean that tells Django to look for templates in application directories
 * ``NAME`` give a name to the engine and use it specifically in a detailed view

To do so, add them as follow:

::

    {
        'BACKEND': '...',
        'DIRS': [...],
        'APP_DIRS': True,
        'NAME': '...',
    }
