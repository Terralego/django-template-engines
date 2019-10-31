import os

from django.test import TestCase, RequestFactory

from template_engines.tests.fake_app.models import Bidon
from template_engines.tests.fake_app.views import DocxTemplateView

from .settings import TEMPLATES_PATH


class TestDocxTemplateView(TestCase):
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
