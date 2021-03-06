How it works ?
==============

Simple template
----------------

These services work like the Django service, so they are subject to the same rules:
 * ``{{ ... }}`` allows you to include variables, consult dictionaries, attributes and list indexs in your templates
 * ``{% ... %}`` allows you to use functions
 * ``{{ ...|... }}`` allows you to use filters

Please consult the Django documentation for more information.

Specific tags and filters by engine
===================================

* ODT and DOCX have specific tags available and auto loaded to handle specific cases

Translate HTML content
----------------------

* Some HTML tags can be translated for ODT and DOCX

example :

```
{{ object.value_html|from_html }}
```

Include images
--------------

Two template tags are available to dynamically include images in generated zip files, one for ODT and the other for DOCX.

For this to work you need to include the binary content of each image in the context transmitted to your template.

Tags are automatically available by type of template (docx_tags and odt_tags).

Now you can add images in the right place:
 * From binary : add your image in the context  ``context[ name of your image ] = {'content': binary of your image}``

     ``{% image_loader image_in_the_context %}`` ,

 Additional arguments are max_width, max_height, request, data, anchor

   ``{% image_loader image_in_the_context max_width="50px" max_height="50px" anchor="as-char" %}``

 * From url :
    * From an url directly :

     ``{% image_url_loader "http://image.png" %}``

    * From the context : add your url in the context like that :
      ``context[ name of your image ] = {'content': binary of your image}``

     ``{% image_url_loader url_in_the_context %}``

    Additional arguments are max_width, max_height, request, data, anchor

     ``{% image_url_loader url_in_the_context max_width="50px" max_height="50px" request="POST" data="" anchor="frame" %}``

max_height and max_width allow to define the maximum your picture should be. It will keep the ratio of the original picture.
It will also not enlarge your picture if you define a value higher than the original picture.

If you need any information about anchor, check http://docs.oasis-open.org/office/v1.2/os/OpenDocument-v1.2-os-part1.html#__RefHeading__1418758_253892949


ODT specific cases
------------------

* Fields :

   To avoid tags and values splitted with Office or Libreoffice editor, use Field to handle custom data except for element in tables

   -> Menu -> Insert -> Field -> Other Field -> put your value here

* Tables :

   If you need to dynamically create tables, do the following:

   .. image:: table_test.png
      :width: 600


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
        template_name = 'path/to/template.odt'
        content_type = 'application/vnd.oasis.opendocument.text'
