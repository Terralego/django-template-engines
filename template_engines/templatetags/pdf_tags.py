import base64

from django import template
from django.utils.safestring import mark_safe

from template_engines.utils import get_content_url, get_extension_picture
from .utils import parse_tag

register = template.Library()


class ImageLoaderURLNode(template.Node):
    def __init__(self, url, data=None, request=None, max_width=None,
                 max_height=None):
        # saves the passed obj parameter for later use
        # this is a template.Variable, because that way it can be resolved
        # against the current context in the render method
        self.url = url
        self.data = data
        self.request = request
        self.max_width = max_width
        self.max_height = max_height

    def render(self, context):
        url, type_request, max_width, max_height, data = self.get_value_context(context)
        response = get_content_url(url, type_request or "get", data)
        if not response:
            return ""
        picture = response.content
        extension = get_extension_picture(picture)
        base64_encoded_data = base64.b64encode(picture)
        base64_message = base64_encoded_data.decode('utf-8')
        return mark_safe(f"data:image/{extension};base64,{base64_message}")

    def get_value_context(self, context):
        final_url = self.url.resolve(context)
        final_request = "get" if not self.request else self.request.resolve(context)
        final_max_width = None if not self.max_width else self.max_width.resolve(context)
        final_max_height = None if not self.max_height else self.max_height.resolve(context)
        final_data = "" if not self.data else self.data.resolve(context)
        return final_url, final_request, final_max_width, final_max_height, final_data


@register.tag
def image_url_loader(parser, token):
    """
    Replace a tag by an image from the url you specified.
    The necessary key is url
    - url : Url where you want to get your picture
    Other keys : data, max_width, max_height, request
    - data : Use it only with post request
    - max_width : Width of the picture rendered
    - max_heigth : Height of the picture rendered
    - request : Type of request, post or get. Get by default.
    """
    tag_name, args, kwargs = parse_tag(token, parser)
    usage = '{{% {tag_name} [url] max_width="5000px" max_height="5000px" ' \
            'request="GET" data="{{"data": "example"}}" %}}'.format(tag_name=tag_name)
    if len(args) > 1 or not all(
            key in ['max_width', 'max_height', 'request', 'data'] for key in kwargs.keys()):
        raise template.TemplateSyntaxError("Usage: %s" % usage)
    return ImageLoaderURLNode(*args, **kwargs)
