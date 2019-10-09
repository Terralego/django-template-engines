from django.template import Template
from django.template.exceptions import TemplateDoesNotExist
from django.test import TestCase

from template_engines.backends.odt import OdtEngine, OdtTemplate
from ..settings import (
    DOCX_TEMPLATE_PATH, ODT_TEMPLATE_PATH,
    TEMPLATES_PATH
)


class TestOdtEngine(TestCase):

    def setUp(self):
        self.params = {
            'NAME': 'odt',
            'DIRS': [TEMPLATES_PATH],
            'APP_DIRS': False,
            'OPTIONS': [],
        }
        self.odt_engine = OdtEngine(self.params)

    def test_get_template_path_works(self):
        self.assertEqual(self.odt_engine.get_template_path(ODT_TEMPLATE_PATH), ODT_TEMPLATE_PATH)

        params_no_specified_dirs_no_app_dirs = {
            'NAME': 'odt',
            'DIRS': [],
            'APP_DIRS': False,
            'OPTIONS': [],
        }
        odt_engine_no_specified_dirs_no_app_dirs = OdtEngine(params_no_specified_dirs_no_app_dirs)
        with self.assertRaises(TemplateDoesNotExist):
            odt_engine_no_specified_dirs_no_app_dirs.get_template_path('template.odt')

        params_dirs_specified = {
            'NAME': 'odt',
            'DIRS': [TEMPLATES_PATH],
            'APP_DIRS': False,
            'OPTIONS': [],
        }
        odt_engine_dirs_specified = OdtEngine(params_dirs_specified)
        self.assertEqual(odt_engine_dirs_specified.get_template_path('template.odt'),
                         ODT_TEMPLATE_PATH)

    def test_get_template_path_bad_template_name(self):
        with self.assertRaises(TemplateDoesNotExist):
            self.odt_engine.get_template_path('bad_name')

    def test_get_template_works(self):
        template = self.odt_engine.get_template(ODT_TEMPLATE_PATH)
        self.assertIsInstance(template, OdtTemplate)
        self.assertIsInstance(template.template, Template)
        self.assertEqual(template.template_path, ODT_TEMPLATE_PATH)

    def test_bad_template(self):
        with self.assertRaises(TemplateDoesNotExist):
            self.odt_engine.get_template(DOCX_TEMPLATE_PATH)
