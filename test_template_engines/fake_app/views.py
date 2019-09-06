from django.views.generic.detail import DetailView

from template_engines.tests.settings import IMAGE_PATH

from .models import Bidon


class OdtTemplateView(DetailView):
    queryset = Bidon.objects.all()
    template_engine = 'odt'
    content_type = 'application/vnd.oasis.opendocument.text'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['image'] = {'content': open(IMAGE_PATH, 'rb').read()}
        context['emtpy_image'] = {'content': b''}
        context['bad_image'] = b''
        context['bad_content_image'] = {'content': 'bad'}
        context['resize'] = {
            'content': open(IMAGE_PATH, 'rb').read(),
            'width': '500pt',
            'height': '500pt'
        }
        return context


class DocxTemplateView(DetailView):
    queryset = Bidon.objects.all()
    template_engine = 'docx'
    content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = {
            'image': {
                'content': open(IMAGE_PATH, 'rb').read(),
                'name': 'michel1',
            },
            'emtpy_image': {
                'content': b'',
                'name': 'michel2',
            },
            'resize': {
                'name': 'michel4',
                'content': open(IMAGE_PATH, 'rb').read(),
                'width': '500pt',
                'height': '500pt'
            },
        }
        return context
