from django.template import Context, Template, TemplateSyntaxError
from django.test import TestCase

from template_engines.templatetags.utils import size_parser, resize

from template_engines.tests.settings import IMAGE_PATH


class TestUtils(TestCase):

    def test_size_parser_no_unit(self):
        self.assertEqual(size_parser(1000), 1000.0)
        self.assertEqual(size_parser('1000'), 1000.0)

    def test_size_parser_dxa(self):
        self.assertEqual(size_parser('1000dxa'), 1000.0)

    def test_size_parser_pt_to_dxa(self):
        self.assertEqual(size_parser('1000pt'), 20000.0)

    def test_size_parser_px_to_dxa(self):
        self.assertEqual(size_parser('1000px'), 15000.0)

    def test_size_parser_in_to_dxa(self):
        self.assertEqual(size_parser('72in'), 103680.0)

    def test_size_parser_cm_to_dxa(self):
        self.assertEqual(size_parser('1cm'), 566.9291338582677)
        self.assertEqual(size_parser('1.5cm'), 850.3937007874015)

    def test_size_parser_emu_to_dxa(self):
        self.assertEqual(size_parser('635emu'), 1.0)

    def test_resize_width_height(self):
        width, height = resize(b'', '100pt', '100pt')
        self.assertEqual(width, 2000.0)
        self.assertEqual(height, 2000.0)
        width, height = resize(b'', '100pt', '100pt', odt=False)
        self.assertEqual(width, 1270000.0)
        self.assertEqual(height, 1270000.0)

    def test_resize_image(self):
        img = open(IMAGE_PATH, 'rb').read()
        width, height = resize(img, None, None)
        self.assertEqual(width, 16697.0)
        self.assertEqual(height, 5763.431472081218)


class TestsDocxURLImageLoader(TestCase):
    def render_template(self, string, context=None):
        context = context or {}
        context = Context(context)
        return Template(string).render(context)

    def test_view_empty_template_tag_name(self):
        self.assertRaisesRegexp(
            TemplateSyntaxError,
            'A name has to be given',
            self.render_template,
            '{% load docx_tags %}'
            '{% docx_image_url_loader %}'
        )

    def test_view_empty_template_tag_url(self):
        self.assertRaisesRegexp(
            TemplateSyntaxError,
            'An url has to be given',
            self.render_template,
            '{% load docx_tags %}'
            '{% docx_image_url_loader name="test" %}'
        )

    def test_view_empty_template_tag_value(self):
        self.assertRaisesRegexp(
            TemplateSyntaxError,
            "name's value not given",
            self.render_template,
            '{% load docx_tags %}'
            '{% docx_image_url_loader name %}'
        )

    def test_view_empty_template_tag_key(self):
        self.assertRaisesRegexp(
            TemplateSyntaxError,
            "You have to put the name of the key in the template",
            self.render_template,
            '{% load docx_tags %}'
            '{% docx_image_url_loader "no_key" %}'
        )

    def test_view_wrong_template_tag_key(self):
        self.assertRaisesRegexp(
            TemplateSyntaxError,
            "wrong_key : this argument doesn't exist",
            self.render_template,
            '{% load docx_tags %}'
            '{% docx_image_url_loader wrong_key="u" %}'
        )

    def test_view_wrong_template_tag_request_type_value(self):
        self.assertRaisesRegexp(
            TemplateSyntaxError,
            "Type of request specified not possible",
            self.render_template,
            '{% load docx_tags %}'
            '{% docx_image_url_loader name="coucou" url="http://wrong_type" request="wrong_type" %}'
        )
