import os

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here,
                       'VERSION.md')) as version_file:
    __version__ = version_file.read().strip()

default_app_config = 'template_engines.apps.TemplateEnginesConfig'
