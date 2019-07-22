Example of use
==============

In a detail view
----------------

In the following exemple, this view will allow any user to fill in the odt
template you specified with a query set object. Will be
available an image that can be loaded with ``libreoffice_image_loader``.

::

    from django.views.generic.detail import DetailView


    class TemplateView(DetailView):
        queryset = AModel.objects.all()
        template_engine = 'odt'
        template_name = 'path'
        content_type = 'application/vnd.oasis.opendocument.text'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['image'] = {'content': open(path, 'rb').read()}
            return context
