import io
import base64
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError
from unittest import mock

from django.template import Context, Template
from django.template.exceptions import TemplateSyntaxError
from django.test import TestCase

from template_engines.templatetags import odt_tags
from template_engines.tests.settings import IMAGE_PATH


class FilterFromHTMLTestCase(TestCase):
    def test_br(self):
        soup = BeautifulSoup('<br>', "html.parser")
        odt_tags.parse_br(soup)
        self.assertEqual("<text:line-break/>", str(soup))

    def test_p(self):
        soup = BeautifulSoup('<p></p>', "html.parser")
        odt_tags.parse_p(soup)
        self.assertEqual("<text:p></text:p>", str(soup))

    def test_a(self):
        soup = BeautifulSoup('<a href="http://test.com">test.com</a>', "html.parser")
        odt_tags.parse_a(soup)
        self.assertEqual('<text:a xlink:href="http://test.com" xlink:type="simple">test.com</text:a>', str(soup))

    @mock.patch('random.randint', return_value=700527536680965024)
    def test_ul(self, randint):
        soup = BeautifulSoup('<ul><li>element 1</li></ul>', "html.parser")
        odt_tags.parse_ul(soup)
        self.assertEqual('<text:list text:style-name="L1" xml:id="list700527536680965024">'
                         '<text:list-item><text:p text:style-name="Standard">element 1</text:p></text:list-item>'
                         '</text:list>', str(soup))

    @mock.patch('random.randint', return_value=700527536680965024)
    def test_ol(self, randint):
        soup = BeautifulSoup('<ol><li>element 1</li></ol>', "html.parser")
        odt_tags.parse_ol(soup)
        self.assertEqual('<text:list text:level="1" text:style-name="L2" xml:id="list700527536680965024">'
                         '<text:list-item><text:p text:style-name="Standard">element 1</text:p></text:list-item>'
                         '</text:list>', str(soup))

    def test_strong(self):
        soup = BeautifulSoup('<strong>Strong</strong>', "html.parser")
        odt_tags.parse_strong(soup)
        self.assertEqual('<text:span text:style-name="BOLD">Strong</text:span>', str(soup))

    def test_em(self):
        soup = BeautifulSoup('<em>Italic</em>', "html.parser")
        odt_tags.parse_italic(soup)
        self.assertEqual('<text:span text:style-name="ITALIC">Italic</text:span>', str(soup))

    def test_u(self):
        soup = BeautifulSoup('<u>Underline</u>', "html.parser")
        odt_tags.parse_underline(soup)
        self.assertEqual('<text:span text:style-name="UNDERLINE">Underline</text:span>', str(soup))

    def test_h(self):
        soup = BeautifulSoup('<h1>Title 1</h1><h2>Title 2</h2><h3>Title 3</h3>', "html.parser")
        odt_tags.parse_h(soup)
        self.assertEqual('<text:h text:outline-level="1">Title 1</text:h>'
                         '<text:h text:outline-level="2">Title 2</text:h>'
                         '<text:h text:outline-level="3">Title 3</text:h>', str(soup))

    def test_html(self):
        html = '<p><br></p>'
        soup = odt_tags.from_html(html)
        self.assertEqual('<text:p><text:line-break/></text:p>', str(soup))


@mock.patch('secrets.token_hex', return_value='test')
class ImageLoaderTestCase(TestCase):
    def test_image_loader_object(self, token):
        context = Context({'image': open(IMAGE_PATH, 'rb').read()})
        template_to_render = Template('{% load odt_tags %}{% image_loader image %}{% image_loader image %}')
        rendered_template = template_to_render.render(context)
        self.assertEqual(rendered_template.count('<draw:frame draw:name="{name}.png"'.format(name=token.return_value)), 2)

    def test_image_loader_resize(self, token):
        context = Context({'image': open(IMAGE_PATH, 'rb').read()})
        template_to_render = Template('{% load odt_tags %}{% image_loader image max_width="100" max_height="100" %}')
        rendered_template = template_to_render.render(context)
        self.assertNotIn('svg:width="16697.0" svg:height="5763.431472081218"', rendered_template)
        self.assertIn('svg:width="100.0" svg:height="34.51776649746193"', rendered_template)

    def test_image_url_loader_resize_one_argument(self, token):
        context = Context({'image': open(IMAGE_PATH, 'rb').read()})
        template_to_render = Template('{% load odt_tags %}{% image_loader image max_height="100" %}')
        rendered_template = template_to_render.render(context)
        self.assertNotIn('svg:width="16697.0" svg:height="5763.431472081218"', rendered_template)
        self.assertIn('svg:width="289.70588235294116" svg:height="100.0"', rendered_template)

    def test_image_loader_fail(self, token):
        with self.assertRaises(TemplateSyntaxError) as cm:
            Template('{% load odt_tags %}{% image_loader image=image %}')
        self.assertEqual('Usage: {% image_loader [image] max_width="5000px" max_height="5000px" '
                         'anchor="as-char" %}', str(cm.exception))

    def test_image_loader_object_base64(self, token):
        context = Context({'image': ';base64,%s' % base64.b64encode(open(IMAGE_PATH, 'rb').read()).decode()})
        template_to_render = Template('{% load odt_tags %}{% image_loader image %}')
        rendered_template = template_to_render.render(context)
        self.assertIn('<draw:frame draw:name="{name}.png"'.format(name=token.return_value), rendered_template)

    def test_image_loader_anchor(self, token):
        context = Context({'image': ';base64,%s' % base64.b64encode(open(IMAGE_PATH, 'rb').read()).decode()})
        template_to_render = Template('{% load odt_tags %}{% image_loader image anchor="as-char" %}')
        rendered_template = template_to_render.render(context)
        self.assertIn('text:anchor-type="as-char"', rendered_template)
        self.assertNotIn('text:anchor-type="paragraph"', rendered_template)


@mock.patch('secrets.token_hex', return_value='test')
class ImageUrlLoaderTestCase(TestCase):
    @mock.patch('requests.get')
    def test_image_url_loader_object(self, mocked_get, token):
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.content = open(IMAGE_PATH, 'rb').read()
        context = Context({'url': "https://test.com"})
        template_to_render = Template('{% load odt_tags %}{% image_url_loader url %}')

        rendered_template = template_to_render.render(context)
        self.assertEqual('<draw:frame draw:name="{name}.png" svg:width="5910.0" svg:height="2040.0" '
                         'text:anchor-type="paragraph" draw:z-index="0">'
                         '<draw:image xlink:href="Pictures/{name}.png" xlink:show="embed" xlink:actuate="onLoad"/>'
                         '</draw:frame>'.format(name=token.return_value), rendered_template)

    @mock.patch('requests.get')
    def test_image_url_loader_url(self, mocked_get, token):
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.content = open(IMAGE_PATH, 'rb').read()
        context = Context({})
        template_to_render = Template('{% load odt_tags %}{% image_url_loader "https://test.com" %}')

        rendered_template = template_to_render.render(context)
        self.assertEqual('<draw:frame draw:name="{name}.png" svg:width="5910.0" svg:height="2040.0" '
                         'text:anchor-type="paragraph" draw:z-index="0">'
                         '<draw:image xlink:href="Pictures/{name}.png" xlink:show="embed" xlink:actuate="onLoad"/>'
                         '</draw:frame>'.format(name=token.return_value), rendered_template)

    @mock.patch('requests.get')
    def test_image_url_loader_resize(self, mocked_get, token):
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.content = open(IMAGE_PATH, 'rb').read()
        context = Context({'url': "https://test.com"})
        template_to_render = Template('{% load odt_tags %}{% image_url_loader url max_width="100" max_height="100" %}')
        rendered_template = template_to_render.render(context)
        self.assertNotIn('svg:width="5910.0" svg:height="2040.0"', rendered_template)
        self.assertIn('svg:width="100.0" svg:height="34.51776649746193"', rendered_template)

    @mock.patch('requests.get')
    def test_image_url_loader_resize_one_argument(self, mocked_get, token):
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.content = open(IMAGE_PATH, 'rb').read()
        context = Context({'url': "https://test.com"})
        template_to_render = Template('{% load odt_tags %}{% image_url_loader url max_height="100" %}')
        rendered_template = template_to_render.render(context)
        self.assertNotIn('svg:width="5910.0" svg:height="2040.0"', rendered_template)
        self.assertIn('svg:width="289.70588235294116" svg:height="100.0"', rendered_template)

    @mock.patch('requests.get')
    def test_image_url_loader_fail(self, mocked_get, token):
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.content = open(IMAGE_PATH, 'rb').read()
        with self.assertRaises(TemplateSyntaxError) as cm:
            Template('{% load odt_tags %}{% image_url_loader url="https://test.com" %}')
        self.assertEqual('Usage: {% image_url_loader [url] max_width="5000px" '
                         'max_height="5000px" request="GET" data="{"data": "example"}" '
                         'anchor="as-char" %}', str(cm.exception))

    @mock.patch('requests.get')
    @mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_image_url_loader_picture_not_accessible(self, mock_out, mocked_get, token):
        mocked_get.return_value.status_code = 404
        mocked_get.return_value.content = b''
        context = Context({})
        template_to_render = Template('{% load odt_tags %}{% image_url_loader "https://test.com" %}')
        template_to_render.render(context)
        self.assertEqual(mock_out.getvalue(), 'The picture is not accessible (Error: 404)\n')

    @mock.patch('requests.get')
    @mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_image_url_loader_picture_connection_error(self, mock_out, mocked_get, token):
        mocked_get.side_effect = ConnectionError
        context = Context({})
        template_to_render = Template('{% load odt_tags %}{% image_url_loader "https://test.com" %}')
        template_to_render.render(context)
        self.assertEqual(mock_out.getvalue(), 'Connection Error, check the url given\n')

    @mock.patch('requests.get')
    @mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_image_url_loader_picture_wrong_request(self, mock_out, mocked_get, token):
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.content = open(IMAGE_PATH, 'rb').read()
        context = Context({})
        template_to_render = Template('{% load odt_tags %}{% image_url_loader "https://test.com" request="WRONG" %}')
        template_to_render.render(context)
        self.assertEqual(mock_out.getvalue(), 'Type of request specified not allowed\n')

    @mock.patch('requests.get')
    @mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_image_url_loader_picture_with_datas(self, mock_out, mocked_get, token):
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.content = open(IMAGE_PATH, 'rb').read()
        context = Context({'data': {'data_to_send': 'bob'}})
        template_to_render = Template('{% load odt_tags %}{% image_url_loader "https://test.com" data=data %}')
        rendered_template = template_to_render.render(context)
        self.assertEqual('<draw:frame draw:name="{name}.png" svg:width="5910.0" svg:height="2040.0" '
                         'text:anchor-type="paragraph" draw:z-index="0">'
                         '<draw:image xlink:href="Pictures/{name}.png" xlink:show="embed" xlink:actuate="onLoad"/>'
                         '</draw:frame>'.format(name=token.return_value), rendered_template)

    @mock.patch('requests.post')
    def test_image_url_loader_picture_post_request(self, mocked_post, token):
        mocked_post.return_value.status_code = 200
        mocked_post.return_value.content = open(IMAGE_PATH, 'rb').read()
        context = Context({})
        template_to_render = Template('{% load odt_tags %}{% image_url_loader "https://test.com" request="POST" %}')
        rendered_template = template_to_render.render(context)
        self.assertEqual('<draw:frame draw:name="{name}.png" svg:width="5910.0" svg:height="2040.0" '
                         'text:anchor-type="paragraph" draw:z-index="0">'
                         '<draw:image xlink:href="Pictures/{name}.png" xlink:show="embed" xlink:actuate="onLoad"/>'
                         '</draw:frame>'.format(name=token.return_value), rendered_template)

    @mock.patch('requests.get')
    def test_image_loader_anchor(self, mocked_get, token):
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.content = open(IMAGE_PATH, 'rb').read()
        context = Context({'image': ';base64,%s' % base64.b64encode(open(IMAGE_PATH, 'rb').read()).decode()})
        template_to_render = Template('{% load odt_tags %}{% image_url_loader "https://test.com" data=data '
                                      'anchor="as-char" %}')
        rendered_template = template_to_render.render(context)
        self.assertIn('text:anchor-type="as-char"', rendered_template)
        self.assertNotIn('text:anchor-type="paragraph"', rendered_template)
