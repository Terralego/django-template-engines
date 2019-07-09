from base64 import b64encode
from io import BytesIO

from django import template
from django.utils.safestring import mark_safe
from magic import from_buffer
from PIL import Image

from .utils import resize

register = template.Library()
IMAGE_MIME_TYPE = ('image/jpeg', 'image/png', 'image/svg+xml')


@register.simple_tag
def libreoffice_image_loader(image):
    """
    Replace a tag by an image you specified.
    You must add an entry to the `context` var that is a dict with at least a `content` key whose
    value is a byte object. You can also specify `width` and `height`, otherwise it will
    automatically resize your image.
    """
    if not isinstance(image, dict):
        return None

    width = image.get('width')
    height = image.get('height')
    content = image.get('content')

    if not isinstance(content, bytes):
        return None

    mime_type = from_buffer(content, mime=True)
    if mime_type not in IMAGE_MIME_TYPE:
        return None

    if not width and not height:
        buffer = BytesIO(content)
        with Image.open(buffer) as img_reader:
            width, height = resize(*img_reader.size)

    return mark_safe(
        f'<draw:frame draw:name="img1" svg:width="{width}" svg:height="{height}">'
        + '<draw:image xlink:type="simple" xlink:show="embed" xlink:actuate="onLoad">'
        + '<office:binary-data>'
        + b64encode(content).decode()
        + '</office:binary-data>'
        + '</draw:image>'
        + '</draw:frame>'
    )
