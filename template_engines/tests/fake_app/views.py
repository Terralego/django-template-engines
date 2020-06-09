from django.views.generic.detail import DetailView

from template_engines.tests.settings import IMAGE_PATH
from .models import Bidon


class OdtTemplateView(DetailView):
    queryset = Bidon.objects.all()
    template_engine = 'odt'
    content_type = 'application/vnd.oasis.opendocument.text'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        with open(IMAGE_PATH, 'rb') as image_file:
            context['image'] = image_file.read()
        context['emtpy_image'] = b''
        context['bad_content_image'] = 'bad'
        return context


class DocxTemplateView(DetailView):
    queryset = Bidon.objects.all()
    template_engine = 'docx'
    content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        with open(IMAGE_PATH, 'rb') as image_file:
            content = image_file.read()
            context['images'] = {
                'image': {
                    'content': content,
                    'name': 'michel1',
                },
                'emtpy_image': {
                    'content': b'',
                    'name': 'michel2',
                },
                'resize': {
                    'name': 'michel4',
                    'content': content,
                    'width': '500pt',
                    'height': '500pt'
                },
            }
        return context


class WeasyprintTemplateView(DetailView):
    queryset = Bidon.objects.all()
    template_engine = 'weasyprint'
    content_type = 'application/pdf'
