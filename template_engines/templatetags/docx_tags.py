import re
import requests

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


class ImageLoaderNode(template.Node):
    def __init__(self, name, url, data=None, width=None, height=None, request="GET"):
        # saves the passed obj parameter for later use
        # this is a template.Variable, because that way it can be resolved
        # against the current context in the render method
        self.name = name
        self.url = url
        self.data = data
        self.width = width
        self.height = height
        self.request = request

    def render(self, context):
        if self.request.lower() == 'get':
            response = requests.get(self.url)
        elif self.request.lower() == 'post':
            response = requests.post(self.url, data=self.data)
        else:
            raise template.TemplateSyntaxError(
                "Type of request specified not possible"
            )
        if response.status_code != 200:
            raise template.TemplateSyntaxError(
                "The picture is not accessible (Error: %s)" % response.status_code
            )
        width, height = resize(response.content, self.width, self.height, odt=False)
        context['images'] = {self.name: {'name': self.name, 'content': response.content}}
        return mark_safe(DOCX_IMAGE.format(self.name, width, height))


def check_keys_docx_image_url_loader(key, value):
    if not key:
        raise template.TemplateSyntaxError(
            "You have to put the name of the key in the template"
        )
    if key not in ['name', 'url', 'width', 'height', 'request', 'data']:
        raise template.TemplateSyntaxError(
            "%s : this argument doesn't exist" % key
        )
    if not value:
        raise template.TemplateSyntaxError(
            "%s's value not given" % key
        )


def check_name_url_docx_image_url_loader(tokens):
    if not tokens.get('name'):
        raise template.TemplateSyntaxError(
            "A name has to be given"
        )
    if not tokens.get('url'):
        raise template.TemplateSyntaxError(
            "An url has to be given"
        )


@register.tag
def docx_image_url_loader(parser, token):
    """
    Replace a tag by an image from the url you specified.
    The necessary keys are : name and url
    - name : Name of your picture, you should not use the same name for 2 differents pictures
           from 2 urls because the second one will overwrite the first one
    - url : Url where you want to get your picture
    Other keys : data, width, height, request
    - data : Use it only with post request
    - width : Width of the picture rendered
    - heigth : Heigth of the picture rendered
    - request : Type of request, post or get. Get by default.
    """

    #  token.split_contents()[0] is docx_image_loader
    contents = token.split_contents()[1:]
    tokens = {}
    for var in contents:
        c1 = re.compile(r'([^"=]+)?([=]?"([^"]+)"|$)')
        match = c1.match(var)
        key = match.group(1)
        value = match.group(3)
        check_keys_docx_image_url_loader(key, value)
        tokens.update({key: value})
    check_name_url_docx_image_url_loader(tokens)
    return ImageLoaderNode(**tokens)
