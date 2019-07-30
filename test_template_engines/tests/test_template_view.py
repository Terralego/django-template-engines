from django.test import TestCase, RequestFactory

from test_template_engines.models import Bidon
from test_template_engines.views import OdtTemplateView, DocxTemplateView


class TestOdtTemplateView(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.object = Bidon.objects.create(name='Michel')
        self.request = self.factory.get('')

    def test_view_works(self):
        OdtTemplateView.template_name = 'test_template_engines/tests/templates/works.odt'
        response = OdtTemplateView.as_view()(self.request, **{'pk': 1}).render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 27160)

    def test_view_works_with_new_line(self):
        OdtTemplateView.template_name = 'test_template_engines/tests/templates/works.odt'
        Bidon.objects.create(name='Michel\nPierre')
        response = OdtTemplateView.as_view()(self.request, **{'pk': 2}).render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 27169)

    def test_view_empty_image(self):
        OdtTemplateView.template_name = 'test_template_engines/tests/templates/empty_image.odt'
        with self.assertRaises(IOError):
            OdtTemplateView.as_view()(self.request, **{'pk': 1}).render()

    def test_view_bad_image(self):
        OdtTemplateView.template_name = 'test_template_engines/tests/templates/bad_image.odt'
        with self.assertRaises(AttributeError):
            OdtTemplateView.as_view()(self.request, **{'pk': 1}).render()

    def test_bad_image_content(self):
        OdtTemplateView.template_name = 'test_template_engines/tests/templates/bad_content_image.odt'
        with self.assertRaises(TypeError):
            OdtTemplateView.as_view()(self.request, **{'pk': 1}).render()

    def test_view_resize(self):
        OdtTemplateView.template_name = 'test_template_engines/tests/templates/resize.odt'
        response = OdtTemplateView.as_view()(self.request, **{'pk': 1}).render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 27133)


class TestDocxTemplateView(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.object = Bidon.objects.create(name='Michel')
        self.request = self.factory.get('')

    def test_view_works(self):
        DocxTemplateView.template_name = 'test_template_engines/tests/templates/works.docx'
        response = DocxTemplateView.as_view()(self.request, **{'pk': 1}).render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 22651)

    def test_view_works_with_new_line(self):
        DocxTemplateView.template_name = 'test_template_engines/tests/templates/works.docx'
        Bidon.objects.create(name='Michel\nPierre')
        response = DocxTemplateView.as_view()(self.request, **{'pk': 2}).render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 22666)

    def test_view_empty_image(self):
        DocxTemplateView.template_name = 'test_template_engines/tests/templates/empty_image.docx'
        with self.assertRaises(IOError):
            DocxTemplateView.as_view()(self.request, **{'pk': 1}).render()

    def test_view_bad_image(self):
        DocxTemplateView.template_name = 'test_template_engines/tests/templates/bad_image.docx'
        with self.assertRaises(AttributeError):
            DocxTemplateView.as_view()(self.request, **{'pk': 1}).render()

    def test_bad_image_content(self):
        DocxTemplateView.template_name = 'test_template_engines/tests/templates/bad_content_image.docx'
        with self.assertRaises(TypeError):
            DocxTemplateView.as_view()(self.request, **{'pk': 1}).render()

    def test_view_resize(self):
        DocxTemplateView.template_name = 'test_template_engines/tests/templates/resize.docx'
        response = DocxTemplateView.as_view()(self.request, **{'pk': 1}).render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 22634)
