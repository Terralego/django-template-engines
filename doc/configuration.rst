Configuration
=============

In the settings, add:

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
            'DIRS': [
                ...
            ],
        },
    ]
