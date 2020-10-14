from pathlib import Path

import weasyprint
from django.template.backends.utils import csrf_input_lazy, csrf_token_lazy
from django.template.context import make_context
from django.template.exceptions import TemplateDoesNotExist

from template_engines import settings as app_settings, settings
from template_engines.backends import AbstractTemplate, BaseEngine


class WeasyprintTemplate(AbstractTemplate):
    def get_base_url(self, request):
        """
        Determine base URL to fetch static and media files from `WEASYPRINT_BASEURL` or
        fall back to using the root path of the URL used in the request.
        """
        return getattr(
            settings, 'WEASYPRINT_BASEURL',
            request.build_absolute_uri('/') if request else '/'
        )

    def render(self, context=None, request=None):
        base_url = self.get_base_url(request)
        if context is None:
            context = {}
        if request is not None:
            context['request'] = request
            context['csrf_input'] = csrf_input_lazy(request)
            context['csrf_token'] = csrf_token_lazy(request)

        html = weasyprint.HTML(
            string=self.template.render(make_context(context)),
            base_url=base_url,
        )
        html.render()
        return html.write_pdf()


class WeasyprintEngine(BaseEngine):
    sub_dirname = app_settings.WEASYPRINT_ENGINE_SUB_DIRNAME
    app_dirname = app_settings.WEASYPRINT_ENGINE_APP_DIRNAME
    template_class = WeasyprintTemplate

    def __init__(self, params):
        params['OPTIONS'].setdefault('builtins', [])
        params['OPTIONS']['builtins'].extend(['template_engines.templatetags.pdf_tags'])
        super().__init__(params)

    def get_template(self, template_name):
        """
        Pdf template are discovered becaused they end by .pdf.html
        Django storage can change suffix to add hash like 'example.pdf_csdfre.html'
        """
        template_path = Path(template_name)
        if template_path.suffix.lower() != '.html':
            if ".pdf" not in template_path.suffixes[0]:
                raise TemplateDoesNotExist('This is not a template PDF file')
        return self.template_class(self.engine.get_template(template_name))
