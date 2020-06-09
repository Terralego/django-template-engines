[![Build Status](https://travis-ci.org/Terralego/django-template-engines.svg?branch=master)](https://travis-ci.org/Terralego/django-template-engines)
[![Maintainability](https://api.codeclimate.com/v1/badges/2b6de132c98427007ab4/maintainability)](https://codeclimate.com/github/Terralego/django-template-engines/maintainability)
[![codecov](https://codecov.io/gh/Terralego/django-template-engines/branch/master/graph/badge.svg)](https://codecov.io/gh/Terralego/django-template-engines)
![Python Version](https://img.shields.io/badge/python-%3E%3D%203.6-blue.svg)
![Django Version](https://img.shields.io/badge/django-%3E%3D%202.2-blue.svg)
[![PyPI version](https://badge.fury.io/py/django-template-engines.svg)](https://badge.fury.io/py/django-template-engines)
[![Documentation Status](https://readthedocs.org/projects/django-template-engines/badge/?version=latest)](https://django-template-engines.readthedocs.io/en/latest/?badge=latest)

# django-template-engines

## Description

Additional template engines for Django.

Generate :

 * PDF (with weasyprint)
 * ODT (beta)
 * DOCX (alpha)

## Requirements

* Weasyprint has specific requirements https://weasyprint.readthedocs.io/en/stable/install.html


## How to use a specific template backend

In the settings, add:

```
INSTALLED_APPS = [
    ...
    'template_engines',
]

...
# Put custom engines before DjangoTemplates Engine (Custom engines will search ONLY template ending with .pdf (weasyprint) .odt (odt) and .docx (docx)
TEMPLATES = [
    {
        'BACKEND': 'template_engines.backends.weasyprint.WeasyprintEngine',
        'APP_DIRS': True,
        'DIRS': [
        ],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
    {
        'BACKEND': 'template_engines.backends.odt.OdtEngine',
        ...,
    },
    {
        'BACKEND': 'template_engines.backends.docx.DocxEngine',
        ...,
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

## Documentation

https://django-template-engines.readthedocs.io/
