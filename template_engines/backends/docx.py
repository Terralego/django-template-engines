from django.conf import settings
from django.template import Context
from django.template.context import make_context

from . import DOCX_PARAGRAPH_RE, TO_CHANGE_RE, DOCX_CHANGES
from .abstract import AbstractTemplate, ZipAbstractEngine
from .utils import modify_libreoffice_doc, add_image_in_docx_template


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
        rendered = self.template.render(Context(context))
        rendered = self.clean(rendered)
        docx_content = modify_libreoffice_doc(self.template_path, 'word/document.xml', rendered)
        for _, image in context.get('images', {}).items():
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
    sub_dirname = getattr(settings, 'DOCX_ENGINE_SUB_DIRNAME', 'docx')
    app_dirname = getattr(settings, 'DOCX_ENGINE_APP_DIRNAME', 'templates')
    template_class = DocxTemplate
    zip_root_file = 'word/document.xml'
