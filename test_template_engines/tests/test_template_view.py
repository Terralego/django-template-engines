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
        self.assertEqual(len(response.content), 27147)

    def test_view_works_with_new_line(self):
        TemplateView.template_name = 'test_template_engines/tests/templates/works.odt'
        Bidon.objects.create(name='Michel\nPierre')
        response = TemplateView.as_view()(self.request, **{'pk': 2}).render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 27155)

    def test_view_empty_image(self):
        TemplateView.template_name = 'test_template_engines/tests/templates/empty_image.odt'
        response = TemplateView.as_view()(self.request, **{'pk': 1}).render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 8560)

    def test_view_bad_image(self):
        TemplateView.template_name = 'test_template_engines/tests/templates/bad_image.odt'
        response = TemplateView.as_view()(self.request, **{'pk': 1}).render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 8609)

    def test_bad_image_content(self):
        TemplateView.template_name = 'test_template_engines/tests/templates/bad_content_image.odt'
        response = TemplateView.as_view()(self.request, **{'pk': 1}).render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 8626)

    def test_view_resize(self):
        TemplateView.template_name = 'test_template_engines/tests/templates/resize.odt'
        response = TemplateView.as_view()(self.request, **{'pk': 1}).render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 27196)
