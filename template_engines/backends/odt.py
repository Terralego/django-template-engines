from re import findall, sub
from zipfile import ZipFile

from django.conf import settings
from django.template import Context
from django.template.context import make_context

from .abstract import AbstractEngine, AbstractTemplate
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

    def clean_new_lines(self, data):
        while len(findall('\n', data)) > 1:
            data = sub(
                '<text:p([^>]+)>([^<\n]*)\n',
                '<text:p\\g<1>>\\g<2></text:p><text:p\\g<1>>',
                data,
            )
        return data

    def render(self, context=None, request=None):
        context = make_context(context, request)
        rendered = self.template.render(Context(context))
        rendered = self.clean(rendered)
        odt_content = modify_libreoffice_doc(self.template_path, 'content.xml', rendered)
        return odt_content


class OdtEngine(AbstractEngine):
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
    mime_type = 'application/vnd.oasis.opendocument.text'

    def get_template_content(self, template_path):
        """
        Returns the contents of a template before modification, as a string.
        """
        with ZipFile(template_path, 'r') as zip_file:
            b_content = zip_file.read('content.xml')
        return b_content.decode()

    def get_template(self, template_name):
        template_path = self.get_template_path(template_name)
        content = self.get_template_content(template_path)
        return self.from_string(content, template_path=template_path)
