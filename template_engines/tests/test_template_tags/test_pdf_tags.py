import base64
import io
from unittest import mock

from django.template import Context, Template
from django.template.exceptions import TemplateSyntaxError
from django.test import TestCase
from requests.exceptions import ConnectionError

from template_engines.tests.settings import IMAGE_PATH


@mock.patch('secrets.token_hex', return_value='test')
class ImageLoaderTestCase(TestCase):
    def test_image_loader_object(self, token):
        with open(IMAGE_PATH, 'rb') as image_file:
            context = Context({'image': image_file.read()})
        template_to_render = Template('{% load pdf_tags %}{% image_loader image %}{% image_loader image %}')
        rendered_template = template_to_render.render(context)
        self.assertEqual(rendered_template.count('<draw:frame draw:name="{name}.png"'.format(name=token.return_value)), 2)

    def test_image_loader_resize(self, token):
        with open(IMAGE_PATH, 'rb') as image_file:
            context = Context({'image': image_file.read()})
        template_to_render = Template('{% load pdf_tags %}{% image_loader image max_width="100" max_height="100" %}')
        rendered_template = template_to_render.render(context)
        self.assertNotIn('svg:width="16697.0" svg:height="5763.431472081218"', rendered_template)
        self.assertIn('svg:width="0.1cm" svg:height="0.03cm"', rendered_template)

    def test_image_url_loader_resize_one_argument(self, token):
        with open(IMAGE_PATH, 'rb') as image_file:
            context = Context({'image': image_file.read()})
        template_to_render = Template('{% load pdf_tags %}{% image_loader image max_height="100" %}')
        rendered_template = template_to_render.render(context)
        self.assertNotIn('svg:width="16697.0" svg:height="5763.431472081218"', rendered_template)
        self.assertIn('svg:width="0.29cm" svg:height="0.1cm"', rendered_template)

    def test_image_loader_fail(self, token):
        with self.assertRaises(TemplateSyntaxError) as cm:
            Template('{% load pdf_tags %}{% image_loader image=image %}')
        self.assertEqual('Usage: {% image_loader [image] max_width="5000px" max_height="5000px" '
                         'anchor="as-char" %}', str(cm.exception))

    def test_image_loader_object_base64(self, token):
        with open(IMAGE_PATH, 'rb') as image_file:
            context = Context({'image': ';base64,%s' % base64.b64encode(image_file.read()).decode()})

        template_to_render = Template('{% load pdf_tags %}{% image_loader image %}')
        rendered_template = template_to_render.render(context)
        self.assertIn('<draw:frame draw:name="{name}.png"'.format(name=token.return_value), rendered_template)

    def test_image_loader_anchor(self, token):
        with open(IMAGE_PATH, 'rb') as image_file:
            context = Context({'image': ';base64,%s' % base64.b64encode(image_file.read()).decode()})
        template_to_render = Template('{% load pdf_tags %}{% image_loader image anchor="as-char" %}')
        rendered_template = template_to_render.render(context)
        self.assertIn('text:anchor-type="as-char"', rendered_template)
        self.assertNotIn('text:anchor-type="paragraph"', rendered_template)


@mock.patch('secrets.token_hex', return_value='test')
class ImageUrlLoaderTestCase(TestCase):
    @mock.patch('requests.get')
    def test_image_url_loader_object(self, mocked_get, token):
        mocked_get.return_value.status_code = 200
        with open(IMAGE_PATH, 'rb') as image_file:
            mocked_get.return_value.content = image_file.read()
        context = Context({'url': "https://test.com"})
        template_to_render = Template('{% load pdf_tags %}{% image_url_loader url %}')

        rendered_template = template_to_render.render(context)
        self.assertTrue(rendered_template.startswith('data:image/png;base64,'))
        self.assertTrue(rendered_template.endswith('=='))

    @mock.patch('requests.get')
    def test_image_url_loader_url(self, mocked_get, token):
        mocked_get.return_value.status_code = 200
        with open(IMAGE_PATH, 'rb') as image_file:
            mocked_get.return_value.content = image_file.read()
        context = Context({})
        template_to_render = Template('{% load pdf_tags %}{% image_url_loader "https://test.com" %}')
        rendered_template = template_to_render.render(context)

        self.assertTrue(rendered_template.startswith('data:image/png;base64,'))
        self.assertTrue(rendered_template.endswith('=='))

    @mock.patch('requests.get')
    def test_image_url_loader_resize(self, mocked_get, token):
        mocked_get.return_value.status_code = 200
        with open(IMAGE_PATH, 'rb') as image_file:
            mocked_get.return_value.content = image_file.read()
        context = Context({'url': "https://test.com"})
        template_to_render = Template('{% load pdf_tags %}{% image_url_loader url max_width="100" max_height="100" %}')
        rendered_template = template_to_render.render(context)
        self.assertTrue(rendered_template.startswith('data:image/png;base64,'))
        self.assertTrue(rendered_template.endswith('=='))

    @mock.patch('requests.get')
    def test_image_url_loader_resize_one_argument(self, mocked_get, token):
        mocked_get.return_value.status_code = 200
        with open(IMAGE_PATH, 'rb') as image_file:
            mocked_get.return_value.content = image_file.read()
        context = Context({'url': "https://test.com"})
        template_to_render = Template('{% load pdf_tags %}{% image_url_loader url max_height="100" %}')
        rendered_template = template_to_render.render(context)
        self.assertTrue(rendered_template.startswith('data:image/png;base64,'))
        self.assertTrue(rendered_template.endswith('=='))

    @mock.patch('requests.get')
    def test_image_url_loader_fail(self, mocked_get, token):
        mocked_get.return_value.status_code = 200
        with open(IMAGE_PATH, 'rb') as image_file:
            mocked_get.return_value.content = image_file.read()
        with self.assertRaises(TemplateSyntaxError) as cm:
            Template('{% load pdf_tags %}{% image_url_loader url="https://test.com" %}')
        self.assertEqual('Usage: {% image_url_loader [url] max_width="5000px" '
                         'max_height="5000px" request="GET" data="{"data": "example"}" '
                         '%}', str(cm.exception))

    @mock.patch('requests.get')
    @mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_image_url_loader_picture_not_accessible(self, mock_out, mocked_get, token):
        mocked_get.return_value.status_code = 404
        mocked_get.return_value.content = b''
        context = Context({})
        template_to_render = Template('{% load pdf_tags %}{% image_url_loader "https://test.com" %}')
        template_to_render.render(context)
        self.assertEqual(mock_out.getvalue(), 'The picture with url : https://test.com is not accessible (Error: 404)\n')

    @mock.patch('requests.get')
    @mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_image_url_loader_picture_connection_error(self, mock_out, mocked_get, token):
        mocked_get.side_effect = ConnectionError
        context = Context({})
        template_to_render = Template('{% load pdf_tags %}{% image_url_loader "https://test.com" %}')
        template_to_render.render(context)
        self.assertEqual(mock_out.getvalue(), 'Connection Error, check the url given (https://test.com)\n')

    @mock.patch('requests.get')
    @mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_image_url_loader_picture_wrong_request(self, mock_out, mocked_get, token):
        mocked_get.return_value.status_code = 200
        with open(IMAGE_PATH, 'rb') as image_file:
            mocked_get.return_value.content = image_file.read()
        context = Context({})
        template_to_render = Template('{% load pdf_tags %}{% image_url_loader "https://test.com" request="WRONG" %}')
        template_to_render.render(context)
        self.assertEqual(mock_out.getvalue(), 'Type of request specified not allowed\n')

    @mock.patch('requests.get')
    @mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_image_url_loader_picture_with_datas(self, mock_out, mocked_get, token):
        mocked_get.return_value.status_code = 200
        with open(IMAGE_PATH, 'rb') as image_file:
            mocked_get.return_value.content = image_file.read()
        context = Context({'data': {'data_to_send': 'bob'}})
        template_to_render = Template('{% load pdf_tags %}{% image_url_loader "https://test.com" data=data %}')
        rendered_template = template_to_render.render(context)
        self.assertTrue(rendered_template.startswith('data:image/png;base64,'))
        self.assertTrue(rendered_template.endswith('=='))

    @mock.patch('requests.post')
    def test_image_url_loader_picture_post_request(self, mocked_post, token):
        mocked_post.return_value.status_code = 200
        with open(IMAGE_PATH, 'rb') as image_file:
            mocked_post.return_value.content = image_file.read()
        context = Context({})
        template_to_render = Template('{% load pdf_tags %}{% image_url_loader "https://test.com" request="POST" %}')
        rendered_template = template_to_render.render(context)
        self.assertTrue(rendered_template.startswith('data:image/png;base64,'))
        self.assertTrue(rendered_template.endswith('=='))
