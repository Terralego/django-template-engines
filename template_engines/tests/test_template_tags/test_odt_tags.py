from bs4 import BeautifulSoup
from unittest import mock

from django.test import TestCase

from template_engines.templatetags import odt_tags


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
