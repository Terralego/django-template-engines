import re
from io import BytesIO

from PIL import Image

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


def automatically_resize(bimage, odt=True):
    """
    Automatically resize the image to fit the page.

    param bimage: an image.
    :type bimage: bytes

    :param odt: Optional
    :type odt: boolean
    """
    buffer = BytesIO(bimage)
    with Image.open(buffer) as img_reader:
        width, height = img_reader.size
        if odt:
            ratio = min(ODT_PAGE_WIDTH / width, ODT_PAGE_HEIGHT / height)
        else:
            ratio = min(DOCX_PAGE_WIDTH / width, DOCX_PAGE_HEIGHT / height)
        return (width * ratio), (height * ratio)


def resize(bimage, width, height, odt=True):
    """
    Automatically resize the image to fit the page. if no width or height has been specified,
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
    if not width and not height:
        width, height = automatically_resize(bimage, odt=odt)
    else:
        width = size_parser(width, odt=odt)
        height = size_parser(height, odt=odt)

    return width, height


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
