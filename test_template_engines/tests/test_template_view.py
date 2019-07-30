from django.test import TestCase, RequestFactory

from test_template_engines.models import Bidon
from test_template_engines.views import TemplateView


class TestTemplateView(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.object = Bidon.objects.create(name='Michel')
        self.request = self.factory.get('')

    def test_view_works(self):
        TemplateView.template_name = 'test_template_engines/tests/templates/works.odt'
        response = TemplateView.as_view()(self.request, **{'pk': 1}).render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 27160)

    def test_view_works_with_new_line(self):
        TemplateView.template_name = 'test_template_engines/tests/templates/works.odt'
        Bidon.objects.create(name='Michel\nPierre')
        response = TemplateView.as_view()(self.request, **{'pk': 2}).render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 27169)

    def test_view_empty_image(self):
        TemplateView.template_name = 'test_template_engines/tests/templates/empty_image.odt'
        with self.assertRaises(IOError):
            TemplateView.as_view()(self.request, **{'pk': 1}).render()

    def test_view_bad_image(self):
        TemplateView.template_name = 'test_template_engines/tests/templates/bad_image.odt'
        with self.assertRaises(AttributeError):
            TemplateView.as_view()(self.request, **{'pk': 1}).render()

    def test_bad_image_content(self):
        TemplateView.template_name = 'test_template_engines/tests/templates/bad_content_image.odt'
        with self.assertRaises(TypeError):
            TemplateView.as_view()(self.request, **{'pk': 1}).render()

    def test_view_resize(self):
        TemplateView.template_name = 'test_template_engines/tests/templates/resize.odt'
        response = TemplateView.as_view()(self.request, **{'pk': 1}).render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 27133)
