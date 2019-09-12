import os

here = os.path.abspath(os.path.dirname(__file__))

__version__ = open(os.path.join(here,
                                'VERSION.md')).read().strip()

default_app_config = 'template_engines.apps.TemplateEnginesConfig'
