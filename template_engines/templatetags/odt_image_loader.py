from base64 import b64encode
from io import BytesIO

from django import template
from django.utils.safestring import mark_safe
from PIL import Image

from .utils import resize

register = template.Library()
ODT_IMAGE = (
    '<draw:frame draw:name="img1" svg:width="{0}" svg:height="{1}">'
    + '<draw:image xlink:type="simple" xlink:show="embed" xlink:actuate="onLoad">'
    + '<office:binary-data>{2}</office:binary-data>'
    + '</draw:image></draw:frame>'
)


@register.simple_tag
def odt_image_loader(image):
    """
    Replace a tag by an image you specified.
    You must add an entry to the ``context`` var that is a dict with at least a ``content`` key
    whose value is a byte object. You can also specify ``width`` and ``height``, otherwise it will
    automatically resize your image.
    """
    width = image.get('width')
    height = image.get('height')
    content = image.get('content')

    if not width and not height:
        buffer = BytesIO(content)
        with Image.open(buffer) as img_reader:
            width, height = resize(*img_reader.size)

    return mark_safe(ODT_IMAGE.format(width, height, b64encode(content).decode()))  # nosec
