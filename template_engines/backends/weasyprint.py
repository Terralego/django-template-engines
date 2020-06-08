import weasyprint
from django.template import RequestContext
from django.template.backends.django import DjangoTemplates, Template
from django.template.backends.utils import csrf_input_lazy, csrf_token_lazy

from template_engines import settings as app_settings, settings


class WeasyprintTemplate(Template):
    def __init__(self, template):
        self.template = template

    def get_base_url(self, request):
        """
        Determine base URL to fetch CSS files from `WEASYPRINT_BASEURL` or
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
            string=self.template.render(RequestContext(context)),
            base_url=base_url,
        )
        html.render()
        return html.write_pdf()


class WeasyprintEngine(DjangoTemplates):
    sub_dirname = app_settings.WEASYPRINT_ENGINE_SUB_DIRNAME
    app_dirname = app_settings.WEASYPRINT_ENGINE_APP_DIRNAME
    template_class = WeasyprintTemplate

    def get_template(self, template_name):
        return self.template_class(self.engine.get_template(template_name))
