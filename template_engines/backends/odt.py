import re

from bs4 import BeautifulSoup
from django.conf import settings
from django.template import Context
from django.template.context import make_context

from .abstract import AbstractTemplate, ZipAbstractEngine
from .utils import modify_libreoffice_doc


class OdtTemplate(AbstractTemplate):
    """
    Handles odt templates.
    """

    def __init__(self, template, template_path=None):
        """
        :param template: the template to fill.
        :type template: django.template.Template

        :param template_path: path to the template.
        :type template_path: str
        """
        super().__init__(template)
        self.template_path = template_path

    def clean(self, data):
        # Add bold style
        enriched_data = re.sub(
            '</office:automatic-styles>',
            (
                '<style:style style:name="BOLD" style:family="text">'
                + '<style:text-properties fo:font-weight="bold" style:font-weight-asian="bold"'
                + ' style:font-weight-complex="bold"/></style:style></office:automatic-styles>'
            ),
            data,
        )

        return enriched_data

    def replace_inputs(self, content):
        """ Replace all text:text-input to text-span """

        soup = BeautifulSoup(content, features='xml')
        input_list = soup.find_all("text:text-input")

        for tag in input_list:
            tag.name = 'span'
            tag.attrs = {}
            for child in tag.findChildren(recursive=False):
                tag.insert_before(child)
            tag.extract()

        return str(soup)

    def render(self, context=None, request=None):
        context = make_context(context, request)
        rendered = self.template.render(Context(context))
        rendered = self.clean(rendered)
        rendered = self.replace_inputs(rendered)
        odt_content = modify_libreoffice_doc(self.template_path, 'content.xml', rendered)
        return odt_content


class OdtEngine(ZipAbstractEngine):
    """
    Odt template engine.

    By default, ``app_dirname`` is equal to 'templates' but you can change this value by adding an
    ``ODT_ENGINE_APP_DIRNAME`` setting in your settings.
    By default, ``sub_dirname`` is equal to 'odt' but you can change this value by adding an
    ``ODT_ENGINE_SUB_DIRNAME`` setting in your settings.
    By default, ``OdtTemplate`` is used as template_class.
    """
    sub_dirname = getattr(settings, 'ODT_ENGINE_SUB_DIRNAME', 'odt')
    app_dirname = getattr(settings, 'ODT_ENGINE_APP_DIRNAME', 'templates')
    template_class = OdtTemplate
    zip_root_file = 'content.xml'
