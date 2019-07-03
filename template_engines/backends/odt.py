from zipfile import ZipFile

from django.conf import settings
from django.template import Context
from django.template.context import make_context

from .abstract import AbstractEngine
from .utils import modify_zip_file


def odt_handler(read_zip_file, write_zip_file, item, rendered):
    if item.filename != 'content.xml':
        write_zip_file.writestr(item, read_zip_file.read(item.filename))
    else:
        write_zip_file.writestr(item, rendered)


class OdtTemplate:
    """
    Handles odt templates.
    """

    def __init__(self, template, **kwargs):
        """
        :param template: the template to fill.
        :type template: django.template.Template

        :param kwargs: it must contain a `template_path`.
        """
        self.template = template
        self.template_path = kwargs.pop('template_path')

    def render(self, context=None, request=None):
        """
        Fills an odt template with the context obtained by combining the `context` and` request` \
parameters and returns an odt file as a byte object.
        """
        context = make_context(context, request)
        rendered = self.template.render(Context(context))
        odt_content = modify_zip_file(self.template_path, odt_handler, rendered)
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
