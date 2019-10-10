import base64

from django import template
from django.core.files.base import ContentFile

from template_engines.odt_helpers import ODT_IMAGE

from base64 import b64encode

from django.utils.safestring import mark_safe

from .utils import resize

register = template.Library()


@register.simple_tag
def image_loader(image):
    """
    Replace a tag by an image you specified.
    You must add an entry to the ``context`` var that is a dict with at least a ``content`` key
    whose value is a byte object. You can also specify ``width`` and ``height``, otherwise it will
    automatically resize your image.
    """
    if isinstance(image, str):
        image = ContentFile(base64.b64decode(image.split(';base64,')[1]))

    width = image.get('width')
    height = image.get('height')
    content = image.get('content')

    width, height = resize(content, width, height)

    return mark_safe(ODT_IMAGE.format(width, height, b64encode(content).decode()))
