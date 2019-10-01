from unittest import mock
import os

from django.template.exceptions import TemplateSyntaxError
from django.test import TestCase, RequestFactory

from template_engines.tests.fake_app.models import Bidon
from template_engines.tests.fake_app.views import OdtTemplateView, DocxTemplateView

from .settings import IMAGE_PATH, TEMPLATES_PATH


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
        self.assertEqual(len(response.content), 59982)

    def test_view_empty_template_tag_name(self):
        DocxTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'docx', 'template_loader_no_name.docx')
        with self.assertRaises(TemplateSyntaxError) as e:
            DocxTemplateView.as_view()(self.request, **{'pk': self.object.pk}).render()
        self.assertEqual(str(e.exception), 'A name has to be given')

    def test_view_empty_template_tag_url(self):
        DocxTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'docx', 'template_loader_no_url.docx')
        with self.assertRaises(TemplateSyntaxError) as e:
            DocxTemplateView.as_view()(self.request, **{'pk': self.object.pk}).render()
        self.assertEqual(str(e.exception), 'An url has to be given')

    def test_view_empty_template_tag_value(self):
        DocxTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'docx', 'template_loader_no_value.docx')
        with self.assertRaises(TemplateSyntaxError) as e:
            DocxTemplateView.as_view()(self.request, **{'pk': self.object.pk}).render()
        self.assertEqual(str(e.exception), "name's value not given")

    def test_view_empty_template_tag_key(self):
        DocxTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'docx', 'template_loader_no_key.docx')
        with self.assertRaises(TemplateSyntaxError) as e:
            DocxTemplateView.as_view()(self.request, **{'pk': self.object.pk}).render()
        self.assertEqual(str(e.exception), "You have to put the name of the key in the template")

    def test_view_wrong_template_tag_key(self):
        DocxTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'docx', 'template_loader_wrong_key.docx')
        with self.assertRaises(TemplateSyntaxError) as e:
            DocxTemplateView.as_view()(self.request, **{'pk': self.object.pk}).render()
        self.assertEqual(str(e.exception), "wrong_key : this argument doesn't exist")

    def test_view_wrong_template_tag_request_type_value(self):
        DocxTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'docx', 'template_loader_wrong_request_type.docx')
        with self.assertRaises(TemplateSyntaxError) as e:
            DocxTemplateView.as_view()(self.request, **{'pk': self.object.pk}).render()
        self.assertEqual(str(e.exception), "Type of request specified not possible")

    @mock.patch('requests.get')
    def test_view_template_tag_get_url(self, mocked):
        def mocked_picture():
            return open(IMAGE_PATH, 'rb').read()
        mocked.return_value.status_code = 200
        mocked.return_value.content = mocked_picture()

        DocxTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'docx', 'template_loader_get_url.docx')
        response = DocxTemplateView.as_view()(self.request, **{'pk': self.object.pk}).render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 23002)

    @mock.patch('requests.post')
    def test_view_template_tag_post_url(self, mocked):
        def mocked_picture():
            return open(IMAGE_PATH, 'rb').read()
        mocked.return_value.status_code = 200
        mocked.return_value.content = mocked_picture()

        DocxTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'docx', 'template_loader_post_url.docx')
        response = DocxTemplateView.as_view()(self.request, **{'pk': self.object.pk}).render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 23099)

    @mock.patch('requests.post')
    def test_view_template_tag_post_url_not_accessible(self, mocked):
        def mocked_picture():
            return open(IMAGE_PATH, 'rb').read()
        mocked.return_value.status_code = 404
        mocked.return_value.content = mocked_picture()

        DocxTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'docx', 'template_loader_post_url.docx')
        with self.assertRaises(TemplateSyntaxError) as e:
            DocxTemplateView.as_view()(self.request, **{'pk': self.object.pk}).render()
        self.assertEqual(str(e.exception), "The picture is not accessible (Error: 404)")

    @mock.patch('requests.get')
    def test_view_template_tag_get_url_wrong_format(self, mocked):
        def mocked_picture():
            return open(IMAGE_PATH, 'rb').read()
        mocked.return_value.status_code = 200
        mocked.return_value.content = mocked_picture()

        DocxTemplateView.template_name = os.path.join(TEMPLATES_PATH, 'docx',
                                                      'template_loader_get_url_wrong_format.docx')
        response = DocxTemplateView.as_view()(self.request, **{'pk': self.object.pk}).render()
        with open('tt.docx', 'wb') as f:
            f.write(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 22989)
