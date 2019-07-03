from os.path import abspath, dirname, join

ROOT = dirname(dirname(dirname(dirname(abspath(__file__)))))
APP_PATH = join(ROOT, 'test_template_engines')
TESTS_PATH = join(APP_PATH, 'tests')
SCREENSHOTS_PATH = join(TESTS_PATH, 'screenshots', 'backends')

ODT_TEMPLATE_PATH = join(ROOT, 'templates', 'odt', 'template.odt')
CONTENT_SCREENSHOT_PATH = join(SCREENSHOTS_PATH, 'content_screenshot.txt')
RENDERED_CONTENT_SCREENSHOT = join(SCREENSHOTS_PATH, 'rendered_content_screenshot.txt')
