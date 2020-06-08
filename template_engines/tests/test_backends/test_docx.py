import os
from io import BytesIO
from zipfile import ZipFile

from django.template import TemplateDoesNotExist, Template
from django.test import TestCase, RequestFactory

from template_engines.backends.docx import DocxEngine, DocxTemplate
from template_engines.tests.fake_app.models import Bidon
from template_engines.tests.fake_app.views import DocxTemplateView
from template_engines.tests.settings import TEMPLATES_PATH, DOCX_TEMPLATE_PATH, DOCX_CONTENT_SCREENSHOT, \
    ODT_TEMPLATE_PATH, DOCX_RENDERED_CONTENT_SCREENSHOT


class DocxEngineTestCase(TestCase):

    def setUp(self):
        self.params = {
            'NAME': 'docx',
            'DIRS': [TEMPLATES_PATH],
            'APP_DIRS': False,
            'OPTIONS': {},
        }
        self.docx_engine = DocxEngine(self.params)

    def test_get_template_path_works(self):
        self.assertEqual(self.docx_engine.get_template_path(DOCX_TEMPLATE_PATH), DOCX_TEMPLATE_PATH)

        params_no_specified_dirs_no_app_dirs = {
            'NAME': 'docx',
            'DIRS': [],
            'APP_DIRS': False,
            'OPTIONS': {},
        }
        docx_engine_no_specified_dirs_no_app_dirs = DocxEngine(params_no_specified_dirs_no_app_dirs)
        with self.assertRaises(TemplateDoesNotExist):
            docx_engine_no_specified_dirs_no_app_dirs.get_template_path('template.docx')

    def test_get_template_path_bad_template_name(self):
        with self.assertRaises(TemplateDoesNotExist):
            self.docx_engine.get_template_path('bad_name')

    def test_get_template_content_works(self):
        self.maxDiff = None
        with open(DOCX_CONTENT_SCREENSHOT, 'r') as read_file:
            self.assertEqual(self.docx_engine.get_template_content(DOCX_TEMPLATE_PATH),
                             read_file.read())

    def test_get_template_works(self):
        template = self.docx_engine.get_template(DOCX_TEMPLATE_PATH)
        self.assertIsInstance(template, DocxTemplate)
        self.assertIsInstance(template.template, Template)
        self.assertEqual(template.template_path, DOCX_TEMPLATE_PATH)

    def test_bad_template(self):
        with self.assertRaises(TemplateDoesNotExist):
            self.docx_engine.get_template(ODT_TEMPLATE_PATH)

    def test_render(self):
        self.maxDiff = None
        template = self.docx_engine.get_template('template.docx')
        rendered = template.render(context={'object': {"name": "Michel"}})
        self.assertIsInstance(rendered, bytes)

        buffer = BytesIO(rendered)
        with ZipFile(buffer, 'r') as zip_read_file:
            with open(DOCX_RENDERED_CONTENT_SCREENSHOT, 'r') as read_file:
                self.assertEqual(zip_read_file.read('word/document.xml').decode(), read_file.read())


class DocxTemplateTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.object = Bidon.objects.create(name='Michel')
        self.request = self.factory.get('')

    def test_view_works(self):
        DocxTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'works.docx')
        response = DocxTemplateView.as_view()(self.request, **{'pk': self.object.pk}).render()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content)

    def test_view_works_with_new_line(self):
        DocxTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'works.docx')
        obj = Bidon.objects.create(name='Michel\nPierre')
        response = DocxTemplateView.as_view()(self.request, **{'pk': obj.pk}).render()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content)

    def test_view_works_with_bold_text(self):
        DocxTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'works.docx')
        obj = Bidon.objects.create(name='Michel <b>Pierre</b>')
        response = DocxTemplateView.as_view()(self.request, **{'pk': obj.pk}).render()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content)

    def test_view_empty_image(self):
        DocxTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'empty_image.docx')
        with self.assertRaises(IOError):
            DocxTemplateView.as_view()(self.request, **{'pk': self.object.pk}).render()

    def test_view_resize(self):
        DocxTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'resize.docx')
        response = DocxTemplateView.as_view()(self.request, **{'pk': self.object.pk}).render()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content)
