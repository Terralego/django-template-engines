import re
from zipfile import ZipFile

from django.conf import settings
from django.template import Context
from django.template.context import make_context

from . import NEW_LINE_TAG, BOLD_START_TAG, BOLD_STOP_TAG
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

    def clean_bold_tag(self, data):
        nb_bold_tag = len(re.findall(BOLD_START_TAG, data))
        if nb_bold_tag > 0:
            data = re.sub(
                '</office:automatic-styles>',
                (
                    '<style:style style:name="BOLD" style:family="text">'
                    + '<style:text-properties fo:font-weight="bold" style:font-weight-asian="bold"'
                    + ' style:font-weight-complex="bold"/></style:style></office:automatic-styles>'
                ),
                data,
            )
            for _ in range(nb_bold_tag):
                data = re.sub(
                    BOLD_START_TAG,
                    '<text:span text:style-name="BOLD">',
                    data,
                )
                data = re.sub(
                    BOLD_STOP_TAG,
                    '</text:span>',
                    data,
                )
        return data

    def clean_new_lines(self, data):
        nb_nl = len(re.findall(NEW_LINE_TAG, data))
        for _ in range(nb_nl):
            data = re.sub(
                '<text:p([^>]+)>([^<{0}]*){0}'.format(NEW_LINE_TAG),
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
