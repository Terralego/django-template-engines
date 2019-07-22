Example of use
==============

In a detail view
----------------

::

    from django.views.generic.detail import DetailView


    class TemplateView(DetailView):
        queryset = AModel.objects.all()
        template_engine = 'odt'
        content_type = 'application/vnd.oasis.opendocument.text'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['image'] = {'content': open(path, 'rb').read()}
            return context
