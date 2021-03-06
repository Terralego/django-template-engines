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

    def test_resize_max_width(self):
        with open(IMAGE_PATH, 'rb') as image_file:
            width, height = resize(image_file.read(), '50', None)
        self.assertEqual(width, "0.05cm")
        self.assertEqual(height, "0.02cm")

    def test_resize_max_height(self):
        with open(IMAGE_PATH, 'rb') as image_file:
            width, height = resize(image_file.read(), None, '50')
        self.assertEqual(width, "0.14cm")
        self.assertEqual(height, "0.05cm")

    def test_resize_max_height_width(self):
        # Original picture is rectangular, we keep the ratio. max_width is smaller than original width
        with open(IMAGE_PATH, 'rb') as image_file:
            width, height = resize(image_file.read(), '50', '50')
        self.assertEqual(width, "0.05cm")
        self.assertEqual(height, "0.02cm")

    def test_resize_max_height_width_2(self):
        # Original picture is rectangular, we keep the ratio. max_height is smaller than original height
        with open(IMAGE_PATH, 'rb') as image_file:
            width, height = resize(image_file.read(), '150', '50')
        self.assertEqual(width, "0.14cm")
        self.assertEqual(height, "0.05cm")

    def test_resize_image(self):
        with open(IMAGE_PATH, 'rb') as image_file:
            img = image_file.read()
        width, height = resize(img, None, None)
        self.assertEqual(width, 5910.0)
        self.assertEqual(height, 2040.0)
