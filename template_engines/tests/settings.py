from os.path import abspath, dirname, join

ROOT = dirname(dirname(dirname(abspath(__file__))))
TESTS_PATH = join(ROOT, 'template_engines', 'tests')
STATIC_PATH = join(ROOT, 'test_template_engines', 'static')
TEMPLATES_PATH = join(STATIC_PATH, 'templates')
SCREENSHOTS_PATH = join(STATIC_PATH, 'screenshots')

ODT_TEMPLATE_PATH = join(TEMPLATES_PATH, 'odt', 'template.odt')
DOCX_TEMPLATE_PATH = join(TEMPLATES_PATH, 'docx', 'template.docx')

CONTENT_SCREENSHOT_PATH = join(SCREENSHOTS_PATH, 'content_screenshot.xml')
DOCX_CONTENT_SCREENSHOT = join(SCREENSHOTS_PATH, 'docx_content_screenshot.xml')
RENDERED_CONTENT_SCREENSHOT = join(SCREENSHOTS_PATH, 'rendered_content_screenshot.txt')
DOCX_RENDERED_CONTENT_SCREENSHOT = join(SCREENSHOTS_PATH, 'docx_rendered_content_screenshot.txt')

IMAGE_PATH = join(STATIC_PATH, 'makina-corpus.png')

XMLS_PATH = join(STATIC_PATH, 'xml')
BAD_TAGS_XML = join(XMLS_PATH, 'bad_tags.xml')
CLEAN_CONTENT = join(XMLS_PATH, 'clean_content.xml')
