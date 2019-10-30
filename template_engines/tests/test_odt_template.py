import os

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
        self.assertTrue(response.content)


class TestOdtTemplateViewWithHTML(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('')
        OdtTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'html.odt')

    def test_br(self):
        obj = Bidon.objects.create(name='<p><br></p>')
        response = OdtTemplateView.as_view()(self.request, **{'pk': obj.pk}).render()
        self.assertEqual(response.status_code, 200)

    def test_a(self):
        obj = Bidon.objects.create(name='<a href="http://test.com">test.com</a>')
        response = OdtTemplateView.as_view()(self.request, **{'pk': obj.pk}).render()
        self.assertEqual(response.status_code, 200)

    def test_ul(self):
        obj = Bidon.objects.create(name='<ul><li>element 1</li></ul>')
        response = OdtTemplateView.as_view()(self.request, **{'pk': obj.pk}).render()
        self.assertEqual(response.status_code, 200)

    def test_ol(self):
        obj = Bidon.objects.create(name='<ol><li>element 1</li></ol>')
        response = OdtTemplateView.as_view()(self.request, **{'pk': obj.pk}).render()
        self.assertEqual(response.status_code, 200)

    def test_strong(self):
        obj = Bidon.objects.create(name='<p><strong>Strong</strong></p>')
        response = OdtTemplateView.as_view()(self.request, **{'pk': obj.pk}).render()
        self.assertEqual(response.status_code, 200)

    def test_em(self):
        obj = Bidon.objects.create(name='<p><em>Strong</em></p>')
        response = OdtTemplateView.as_view()(self.request, **{'pk': obj.pk}).render()
        self.assertEqual(response.status_code, 200)

    def test_u(self):
        obj = Bidon.objects.create(name='<p><u>Strong</u></p>')
        response = OdtTemplateView.as_view()(self.request, **{'pk': obj.pk}).render()
        self.assertEqual(response.status_code, 200)

    def test_h(self):
        obj = Bidon.objects.create(name='<h1>Title 1</h1><h2>Title 2</h2><h3>Title 3</h3>')
        response = OdtTemplateView.as_view()(self.request, **{'pk': obj.pk}).render()
        self.assertEqual(response.status_code, 200)
