import base64

from django import template

from template_engines.odt_helpers import ODT_IMAGE
from django.utils.safestring import mark_safe

from .utils import resize

register = template.Library()


@register.simple_tag
def image_loader(image, i_width=None, i_height=None):
    """
    Replace a tag by an image you specified.
    You must add an entry to the ``context`` var that is a dict with at least a ``content`` key
    whose value is a byte object. You can also specify ``width`` and ``height``, otherwise it will
    automatically resize your image.
    """
    if isinstance(image, str):
        if image:
            image = {'content': base64.b64decode(image.split(';base64,')[1])}
        else:
            return
    width = i_width or image.get('width')
    height = i_height or image.get('height')
    content = image.get('content')

    width, height = resize(content, width, height)

    return mark_safe(ODT_IMAGE.format(width, height, base64.b64encode(content).decode()))
