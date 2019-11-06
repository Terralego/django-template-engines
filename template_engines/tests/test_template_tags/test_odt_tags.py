from bs4 import BeautifulSoup
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
        context = Context({'image': {'content': open(IMAGE_PATH, 'rb').read()}})
        template_to_render = Template('{% load odt_tags %}{% image_loader image %}{% image_loader image %}')
        rendered_template = template_to_render.render(context)
        self.assertEqual(rendered_template.count('<draw:frame draw:name="{name}"'.format(name=token.return_value)), 2)

    def test_image_loader_resize(self, token):
        context = Context({'image': {'content': open(IMAGE_PATH, 'rb').read()}})
        template_to_render = Template('{% load odt_tags %}{% image_loader image width="32" height="42" %}')
        rendered_template = template_to_render.render(context)
        self.assertNotIn('svg:width="16697.0" svg:height="5763.431472081218"', rendered_template)
        self.assertIn('svg:width="32.0" svg:height="42.0"', rendered_template)

    def test_image_url_loader_fail(self, token):
        with self.assertRaises(TemplateSyntaxError) as cm:
            Template('{% load odt_tags %}{% image_loader image=image %}')
        self.assertEqual('Usage: {% image_loader [image] width="5000" height="5000" %}', str(cm.exception))


@mock.patch('secrets.token_hex', return_value='test')
class ImageUrlLoaderTestCase(TestCase):
    @mock.patch('requests.get')
    def test_image_url_loader_object(self, mocked_get, token):
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.content = open(IMAGE_PATH, 'rb').read()
        context = Context({'url': "https://test.com"})
        template_to_render = Template('{% load odt_tags %}{% image_url_loader url %}')

        rendered_template = template_to_render.render(context)
        self.assertEqual('<draw:frame draw:name="{name}" svg:width="16697.0" svg:height="5763.431472081218" '
                         'text:anchor-type="paragraph" draw:z-index="0" text:anchor-type="paragraph">'
                         '<draw:image xlink:href="Pictures/{name}" xlink:show="embed" xlink:actuate="onLoad">'
                         '</draw:image></draw:frame>'.format(name=token.return_value), rendered_template)

    @mock.patch('requests.get')
    def test_image_url_loader_url(self, mocked_get, token):
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.content = open(IMAGE_PATH, 'rb').read()
        context = Context({})
        template_to_render = Template('{% load odt_tags %}{% image_url_loader "https://test.com" %}')

        rendered_template = template_to_render.render(context)
        self.assertEqual('<draw:frame draw:name="{name}" svg:width="16697.0" svg:height="5763.431472081218" '
                         'text:anchor-type="paragraph" draw:z-index="0" text:anchor-type="paragraph">'
                         '<draw:image xlink:href="Pictures/{name}" xlink:show="embed" xlink:actuate="onLoad">'
                         '</draw:image></draw:frame>'.format(name=token.return_value), rendered_template)

    @mock.patch('requests.get')
    def test_image_url_loader_fail(self, mocked_get, token):
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.content = open(IMAGE_PATH, 'rb').read()
        with self.assertRaises(TemplateSyntaxError) as cm:
            Template('{% load odt_tags %}{% image_url_loader url="https://test.com" %}')
        self.assertEqual('Usage: {% image_url_loader [url] width="5000" '
                         'height="5000" request="GET" data="{"data": "example"}"%}', str(cm.exception))

    @mock.patch('requests.get')
    def test_image_url_loader_picture_not_accessible(self, mocked_get, token):
        mocked_get.return_value.status_code = 404
        mocked_get.return_value.content = b''
        context = Context({})
        template_to_render = Template('{% load odt_tags %}{% image_url_loader "https://test.com" %}')
        with self.assertRaises(TemplateSyntaxError) as cm:
            template_to_render.render(context)
        self.assertEqual('The picture is not accessible (Error: 404)', str(cm.exception))

    @mock.patch('requests.get')
    def test_image_url_loader_picture_wrong_request(self, mocked_get, token):
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.content = open(IMAGE_PATH, 'rb').read()
        context = Context({})
        template_to_render = Template('{% load odt_tags %}{% image_url_loader "https://test.com" request="WRONG" %}')
        with self.assertRaises(TemplateSyntaxError) as cm:
            template_to_render.render(context)
        self.assertEqual('Type of request specified not allowed', str(cm.exception))

    @mock.patch('requests.post')
    def test_image_url_loader_picture_post_request(self, mocked_post, token):
        mocked_post.return_value.status_code = 200
        mocked_post.return_value.content = open(IMAGE_PATH, 'rb').read()
        context = Context({})
        template_to_render = Template('{% load odt_tags %}{% image_url_loader "https://test.com" request="POST" %}')
        rendered_template = template_to_render.render(context)
        self.assertEqual('<draw:frame draw:name="{name}" svg:width="16697.0" svg:height="5763.431472081218" '
                         'text:anchor-type="paragraph" draw:z-index="0" text:anchor-type="paragraph">'
                         '<draw:image xlink:href="Pictures/{name}" xlink:show="embed" xlink:actuate="onLoad">'
                         '</draw:image></draw:frame>'.format(name=token.return_value), rendered_template)
