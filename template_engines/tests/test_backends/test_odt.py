import io
import os
from unittest import mock

from django.template import Template
from django.template.exceptions import TemplateDoesNotExist
from django.test import TestCase, RequestFactory

from template_engines.backends.odt import OdtEngine, OdtTemplate
from ..fake_app.models import Bidon
from ..fake_app.views import OdtTemplateView
from ..settings import (
    DOCX_TEMPLATE_PATH, IMAGE_PATH,
    TEMPLATES_PATH, ODT_TEMPLATE_PATH
)


class OdtEngineTestCase(TestCase):
    def setUp(self):
        self.params = {
            'NAME': 'odt',
            'DIRS': [TEMPLATES_PATH],
            'APP_DIRS': False,
            'OPTIONS': {},
        }
        self.odt_engine = OdtEngine(self.params)

    def test_get_template_path_works(self):
        self.assertEqual(self.odt_engine.get_template_path(ODT_TEMPLATE_PATH), ODT_TEMPLATE_PATH)

        params_no_specified_dirs_no_app_dirs = {
            'NAME': 'odt',
            'DIRS': [],
            'APP_DIRS': False,
            'OPTIONS': {},
        }
        odt_engine_no_specified_dirs_no_app_dirs = OdtEngine(params_no_specified_dirs_no_app_dirs)
        with self.assertRaises(TemplateDoesNotExist):
            odt_engine_no_specified_dirs_no_app_dirs.get_template_path('template.odt')

        params_dirs_specified = {
            'NAME': 'odt',
            'DIRS': [TEMPLATES_PATH],
            'APP_DIRS': False,
            'OPTIONS': {},
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


class OdtTemplateTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.object = Bidon.objects.create(name='Michel')
        self.request = self.factory.get('')

    def test_view_works(self):
        OdtTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'works.odt')
        response = OdtTemplateView.as_view()(self.request, **{'pk': self.object.pk}).render()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content)

    def test_view_works_with_new_line(self):
        OdtTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'works.odt')
        obj = Bidon.objects.create(name='Michel\nPierre')
        response = OdtTemplateView.as_view()(self.request, **{'pk': obj.pk}).render()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content)

    def test_view_works_with_from_html(self):
        OdtTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'html.odt')
        obj = Bidon.objects.create(name='<p>Michel\nPierre</p>')
        response = OdtTemplateView.as_view()(self.request, **{'pk': obj.pk}).render()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content)

    @mock.patch('requests.get',)
    @mock.patch('template_engines.templatetags.utils.urlopen')
    def test_view_works_with_from_html_with_image(self, mock_url, mocked_get):
        mocked_get.return_value.status_code = 200
        with open(IMAGE_PATH, 'rb') as image_file:
            mocked_get.return_value.content = image_file.read()
        image_file = open(IMAGE_PATH, 'rb')
        mock_url.return_value = image_file
        setattr(image_file, 'headers', {'content-length': 100})
        OdtTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'html.odt')
        obj = Bidon.objects.create(name='<img src="http://images.com/monimage.jpeg">')
        response = OdtTemplateView.as_view()(self.request, **{'pk': obj.pk}).render()
        image_file.close()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content)

    def test_view_works_with_bold_text(self):
        OdtTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'works.odt')
        obj = Bidon.objects.create(name='Michel <b>Pierre</b>')
        response = OdtTemplateView.as_view()(self.request, **{'pk': obj.pk}).render()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content)

    @mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_view_empty_image(self, mock_out):
        OdtTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'empty_image.odt')
        OdtTemplateView.as_view()(self.request, **{'pk': self.object.pk}).render()
        self.assertEqual(mock_out.getvalue(), "emtpy_image is not a valid picture\n")

    @mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_bad_image_content(self, mock_out):
        OdtTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'bad_content_image.odt')
        OdtTemplateView.as_view()(self.request, **{'pk': self.object.pk}).render()
        self.assertEqual(mock_out.getvalue(), "bad_content_image is not a valid picture\n")

    def test_view_resize(self):
        OdtTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'resize.odt')
        response = OdtTemplateView.as_view()(self.request, **{'pk': self.object.pk}).render()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content)
