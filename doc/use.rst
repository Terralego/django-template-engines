How it works ?
===============

Simple template
----------------

These services work like the Django service, so they are subject to the same rules:
 * ``{{ ... }}`` allows you to include variables, consult dictionaries, attributes and list indexs in your templates
 * ``{% ... %}`` allows you to use functions
 * ``{{ ...|... }}`` allows you to use filters

Please consult the Django documentation for more information.

Include images
--------------

Two template tags are available to dynamically include images, one for ODT and the other for DOCX.

For this to work you need to include the binary content of each image in the context transmitted to your template.

Then at the top of your template, you must add ``{% load docx_tags %}`` if it is a DOCX template or
``{% load odt_tags %}`` if it is an ODT template.

Now you can add images by using ``{% image_loader image_name_in_the_context %}`` in the right place.

Example of easy use of the ODT engine
-------------------------------------

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
