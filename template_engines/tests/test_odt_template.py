import io
import os
from unittest import mock

from django.test import TestCase, RequestFactory

from template_engines.tests.fake_app.models import Bidon
from template_engines.tests.fake_app.views import OdtTemplateView

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
        self.assertTrue(response.content)

    def test_view_works_with_new_line(self):
        OdtTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'works.odt')
        obj = Bidon.objects.create(name='Michel\nPierre')
        response = OdtTemplateView.as_view()(self.request, **{'pk': obj.pk}).render()
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
