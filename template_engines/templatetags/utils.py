import re
from io import BytesIO
from urllib.request import urlopen

from PIL import Image, ImageFile
from django.template.base import FilterExpression, kwarg_re

DIM_REGEX = r'^(?P<v>(\d|\.)+)(?P<u>[a-z]*)$'

DOCX_PAGE_WIDTH = 6120130
DOCX_PAGE_HEIGHT = 9251950

ODT_PAGE_WIDTH = 16697
ODT_PAGE_HEIGHT = 28815

CONV_MAPPING = {
    '': lambda v: v,
    'dxa': lambda v: v,
    'pt': lambda v: v * 20,
    'px': lambda v: (v * 0.75) * 20,
    'in': lambda v: v * 72 * 20,
    'cm': lambda v: (v / 2.54) * 72 * 20,
    'emu': lambda v: v / 635,
}


def size_to_odt(width, height):
    width = CONV_MAPPING['px'](width)
    height = CONV_MAPPING['px'](height)
    return width, height


def size_parser(dim, odt=True):
    """
    Convert `dxa`, `pt`, `px`, `in`, `cm`, `emu` to `dxa` if odt else to `emu`.

    :param dim: {value}{unit}
    :type dim: str
    """
    if isinstance(dim, int):
        return dim

    find_dim = re.search(DIM_REGEX, dim)
    value = float(find_dim.group('v'))
    unit = find_dim.group('u')

    if odt:
        return CONV_MAPPING[unit](value)
    else:
        return CONV_MAPPING[unit](value) * 635


def get_final_width_height(max_width, max_height, width, height):
    ratio = width / height

    max_width = min(val for val in [max_width, width] if val is not None)
    max_height = min(val for val in [max_height, height] if val is not None)

    if max_width != width or max_height != height:
        tmp_height = max_width / ratio
        tmp_width = max_height * ratio
        if tmp_height < max_height:
            height = tmp_height
            width = max_width
        elif tmp_width < max_width:
            width = tmp_width
            height = max_height

    return width, height


def resize_keep_ratio(bimage, max_width, max_height, odt=True):
    buffer = BytesIO(bimage)
    with Image.open(buffer) as img_reader:
        width, height = img_reader.size

    if odt:
        width, height = size_to_odt(width, height)

    final_width, final_height = get_final_width_height(max_width, max_height, width, height)

    return final_width, final_height


def resize(bimage, max_width, max_height, odt=True):
    """
    Resize the image with max_width or/and max_height has been specified,
    otherwise convert them.

    :param bimage: an image.
    :type bimage: bytes

    :param width: {value}{unit}
    :type width: str

    :param height: {value}{unit}
    :type height: str

    :param odt: Optional
    :type odt: boolean
    """
    if not max_width and not max_height:
        buffer = BytesIO(bimage)
        with Image.open(buffer) as img_reader:
            width, height = img_reader.size
            if odt:
                width, height = size_to_odt(width, height)
        return width, height

    if max_width:
        max_width = size_parser(max_width, odt=odt)
    if max_height:
        max_height = size_parser(max_height, odt=odt)
    width, height = resize_keep_ratio(bimage, max_width, max_height)

    return f"{round(width / 1000, 2)}cm", f"{round(height / 1000, 2)}cm"


def parse_tag(token, parser):
    """
    Generic template tag parser.

    Returns a three-tuple: (tag_name, args, kwargs)

    tag_name is a string, the name of the tag.

    args is a list of FilterExpressions, from all the arguments that didn't look like kwargs,
    in the order they occurred, including any that were mingled amongst kwargs.

    kwargs is a dictionary mapping kwarg names to FilterExpressions, for all the arguments that
    looked like kwargs, including any that were mingled amongst args.

    (At rendering time, a FilterExpression f can be evaluated by calling f.resolve(context).)
    """
    # Split the tag content into words, respecting quoted strings.
    bits = token.split_contents()

    # Pull out the tag name.
    tag_name = bits.pop(0)

    # Parse the rest of the args, and build FilterExpressions from them so that
    # we can evaluate them later.
    args = []
    kwargs = {}
    for bit in bits:
        bit = bit.replace('&quot;', '"')
        # Is this a kwarg or an arg?
        match = kwarg_re.match(bit)
        kwarg_format = match and match.group(1)
        if kwarg_format:
            key, value = match.groups()
            kwargs[key] = FilterExpression(value, parser)
        else:
            args.append(FilterExpression(bit, parser))

    return tag_name, args, kwargs


def get_image_infos_from_uri(uri):
    """ get image size and dimensions """
    if not uri.lower().startswith('http'):
        # protect use of urlopen from filesystem read
        return None, (None, None), None

    file = urlopen(uri)
    size = file.headers.get("content-length")
    dimensions = (None, None)
    mime_type = None

    if size:
        size = int(size)
    p = ImageFile.Parser()
    while True:
        data = file.read(1024)
        if not data:
            break
        p.feed(data)
        if p.image:
            dimensions = p.image.size
            mime_type = f"image/{p.image.format.lower()}"
            break

    file.close()
    return size, dimensions, mime_type
