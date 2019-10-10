from django import template
from django.utils.safestring import mark_safe

from .utils import resize

register = template.Library()

DOCX_IMAGE = (
    '</w:t>'
    + '</w:r>'
    + '</w:p>'
    + '<w:p>'
    + '<w:r>'
    + '<w:drawing>'
    + '<wp:anchor behindDoc="0" distT="0" distB="0" distL="0" distR="0" simplePos="0" locked="0"'
    + ' layoutInCell="1" allowOverlap="1" relativeHeight="2">'
    + '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
    + '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
    + '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
    + '<pic:blipFill>'
    + '<a:blip r:embed="{0}">'
    + '</a:blip>'
    + '<a:stretch>'
    + '<a:fillRect/>'
    + '</a:stretch>'
    + '</pic:blipFill>'
    + '<pic:spPr bwMode="auto">'
    + '<a:xfrm>'
    + '<a:off x="0" y="0"/>'
    + '<a:ext cx="{1}" cy="{2}"/>'
    + '</a:xfrm>'
    + '<a:prstGeom prst="rect">'
    + '<a:avLst/>'
    + '</a:prstGeom>'
    + '</pic:spPr>'
    + '</pic:pic>'
    + '</a:graphicData>'
    + '</a:graphic>'
    + '</wp:anchor>'
    + '</w:drawing>'
    + '</w:r>'
    + '</w:p>'
    + '<w:p>'
    + '<w:r>'
    + '<w:t>'
)


@register.simple_tag
def image_loader(image):
    """
    Replace a tag by an image you specified.
    You must add an entry to the ``context`` var that is a dict with ``'images'`` as key and other
    dicts in it with at least a ``content`` key whose value is a byte object and a ``name`` key.
    You can also specify ``width`` and ``height``,
    otherwise it will automatically resize your image.
    """
    name = image.get('name')
    width = image.get('width')
    height = image.get('height')
    content = image.get('content')

    width, height = resize(content, width, height, odt=False)

    return mark_safe(DOCX_IMAGE.format(name, width, height))  # nosec
