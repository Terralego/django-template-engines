from os.path import abspath, dirname, join

ROOT = dirname(dirname(dirname(abspath(__file__))))
TESTS_PATH = join(ROOT, 'template_engines', 'tests')
FAKE_APP_PATH = join(TESTS_PATH, 'fake_app')
DATA_PATH = join(FAKE_APP_PATH, 'data')
TEMPLATES_PATH = join(FAKE_APP_PATH, 'templates')
SCREENSHOTS_PATH = join(DATA_PATH, 'screenshots')

ODT_TEMPLATE_PATH = join(TEMPLATES_PATH, 'odt', 'template.odt')
DOCX_TEMPLATE_PATH = join(TEMPLATES_PATH, 'docx', 'template.docx')
PDF_TEMPLATE_PATH = join(TEMPLATES_PATH, 'pdf', 'template.pdf')

CONTENT_SCREENSHOT_PATH = join(SCREENSHOTS_PATH, 'content_screenshot.xml')
DOCX_CONTENT_SCREENSHOT = join(SCREENSHOTS_PATH, 'docx_content_screenshot.xml')
RENDERED_CONTENT_SCREENSHOT = join(SCREENSHOTS_PATH, 'rendered_content_screenshot.txt')
DOCX_RENDERED_CONTENT_SCREENSHOT = join(SCREENSHOTS_PATH, 'docx_rendered_content_screenshot.txt')

IMAGE_PATH = join(DATA_PATH, 'makina-corpus.png')

XML_PATH = join(DATA_PATH, 'xml')
BAD_TAGS_XML = join(XML_PATH, 'bad_tags.xml')
CLEAN_CONTENT = join(XML_PATH, 'clean_content.xml')
