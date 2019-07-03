from django.views.generic.detail import BaseDetailView

from .mixins.abstract import AbstractTemplateResponseMixin
from .mixins.single_object import SingleObjectMixin
from .responses.to_pdf import ToPdfResponse
from .models import Bidon


class TemplateView(AbstractTemplateResponseMixin, SingleObjectMixin,
                   BaseDetailView):
    queryset = Bidon.objects.all()
    template_engine = 'odt'
    response_class = ToPdfResponse
    content_type = 'application/pdf'

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
