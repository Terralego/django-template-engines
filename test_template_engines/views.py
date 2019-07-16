from django.views.generic.detail import DetailView

from .models import Bidon


class TemplateView(DetailView):
    queryset = Bidon.objects.all()
    template_engine = 'odt'
    content_type = 'application/vnd.oasis.opendocument.text'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['image'] = {'content': open('test_template_engines/makina-corpus.png', 'rb').read()}
        context['emtpy_image'] = {'content': b''}
        context['bad_image'] = b''
        context['bad_content_image'] = {'content': 'bad'}
        context['resize'] = {
            'content': open('test_template_engines/makina-corpus.png', 'rb').read(),
            'width': 500,
            'height': 500
        }
        return context
