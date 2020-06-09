from pathlib import Path

from bs4 import BeautifulSoup
from django.template.context import make_context
from django.template.exceptions import TemplateDoesNotExist

from template_engines import settings as app_settings
from template_engines.utils import modify_content_document
from template_engines.utils.docx import add_image_in_docx_template, DOCX_PARAGRAPH_RE, DOCX_CHANGES, TO_CHANGE_RE
from . import AbstractTemplate, ZipAbstractEngine


class DocxTemplate(AbstractTemplate):
    """
    Handles docx templates.
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
        return DOCX_PARAGRAPH_RE.sub(
            lambda e: TO_CHANGE_RE.sub(
                lambda x: DOCX_CHANGES[x.group(0)].format(e.group(1)),
                e.group(0),
            ),
            data,
        )

    def render(self, context=None, request=None):
        """
        Fills a docx template with the context obtained by combining the `context` and` request`
        parameters and returns a docx file as a byte object.
        """
        context = make_context(context, request)
        rendered = self.template.render(context)
        rendered = self.clean(rendered)
        soup = BeautifulSoup(rendered, features='html.parser')
        docx_content = modify_content_document(self.template_path, ['word/document.xml'], soup)
        for key, image in context.get('images', {}).items():
            docx_content = add_image_in_docx_template(docx_content, image)
        return docx_content


class DocxEngine(ZipAbstractEngine):
    """
    Docx template engine.

    ``app_dirname`` is equal to 'templates' but you can change this value by adding
    an ``DOCX_ENGINE_APP_DIRNAME`` setting in your settings.
    By default, ``sub_dirname`` is equal to 'docx' but you can change this value by adding
    an ``DOCX_ENGINE_SUB_DIRNAME`` setting in your settings.
    By default, ``DocxTemplate`` is used as template_class.
    """
    sub_dirname = app_settings.DOCX_ENGINE_SUB_DIRNAME
    app_dirname = app_settings.DOCX_ENGINE_APP_DIRNAME
    template_class = DocxTemplate
    zip_root_files = ['word/document.xml']

    def __init__(self, params):
        params['OPTIONS'].setdefault('builtins', [])
        params['OPTIONS']['builtins'].extend(['template_engines.templatetags.docx_tags'])
        super().__init__(params)

    def get_template_path(self, filename):
        path = super().get_template_path(filename)
        path_object = Path(path)
        if path_object.suffix.lower() != '.docx':
            raise TemplateDoesNotExist('This is not a DOCX file')
        return path
