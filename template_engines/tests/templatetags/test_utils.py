from django.test import TestCase

from template_engines.templatetags.utils import size_parser, resize

from ..settings import IMAGE_PATH


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
