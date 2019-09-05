import os

from django.test import TestCase, RequestFactory

from test_template_engines.fake_app.models import Bidon
from test_template_engines.fake_app.views import OdtTemplateView, DocxTemplateView

from .settings import TEMPLATES_PATH


class TestOdtTemplateView(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.object = Bidon.objects.create(name='Michel')
        self.request = self.factory.get('')

    def test_view_works(self):
        OdtTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'works.odt')
        response = OdtTemplateView.as_view()(self.request, **{'pk': self.object.pk}).render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 27160)

    def test_view_works_with_new_line(self):
        OdtTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'works.odt')
        obj = Bidon.objects.create(name='Michel\nPierre')
        response = OdtTemplateView.as_view()(self.request, **{'pk': obj.pk}).render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 27169)

    def test_view_works_with_bold_text(self):
        OdtTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'works.odt')
        obj = Bidon.objects.create(name='Michel <b>Pierre</b>')
        response = OdtTemplateView.as_view()(self.request, **{'pk': obj.pk}).render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 27226)

    def test_view_empty_image(self):
        OdtTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'empty_image.odt')
        with self.assertRaises(IOError):
            OdtTemplateView.as_view()(self.request, **{'pk': self.object.pk}).render()

    def test_view_bad_image(self):
        OdtTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'bad_image.odt')
        with self.assertRaises(AttributeError):
            OdtTemplateView.as_view()(self.request, **{'pk': self.object.pk}).render()

    def test_bad_image_content(self):
        OdtTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'bad_content_image.odt')
        with self.assertRaises(TypeError):
            OdtTemplateView.as_view()(self.request, **{'pk': self.object.pk}).render()

    def test_view_resize(self):
        OdtTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'resize.odt')
        response = OdtTemplateView.as_view()(self.request, **{'pk': self.object.pk}).render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 27137)


class TestDocxTemplateView(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.object = Bidon.objects.create(name='Michel')
        self.request = self.factory.get('')

    def test_view_works(self):
        DocxTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'works.docx')
        response = DocxTemplateView.as_view()(self.request, **{'pk': self.object.pk}).render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 41742)

    def test_view_works_with_new_line(self):
        DocxTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'works.docx')
        obj = Bidon.objects.create(name='Michel\nPierre')
        response = DocxTemplateView.as_view()(self.request, **{'pk': obj.pk}).render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 41753)

    def test_view_works_with_bold_text(self):
        DocxTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'works.docx')
        obj = Bidon.objects.create(name='Michel <b>Pierre</b>')
        response = DocxTemplateView.as_view()(self.request, **{'pk': obj.pk}).render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 41775)

    def test_view_empty_image(self):
        DocxTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'empty_image.docx')
        with self.assertRaises(IOError):
            DocxTemplateView.as_view()(self.request, **{'pk': self.object.pk}).render()

    def test_view_resize(self):
        DocxTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'resize.docx')
        response = DocxTemplateView.as_view()(self.request, **{'pk': self.object.pk}).render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 59982)
