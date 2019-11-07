import logging
import secrets
import random
import re
import requests

from bs4 import BeautifulSoup
from django import template
from django.template.base import FilterExpression
from django.utils.safestring import mark_safe

from template_engines.backends.utils_odt import ODT_IMAGE
from .utils import parse_tag, resize

register = template.Library()

logger = logging.getLogger(__name__)


def parse_p(soup):
    """ Replace p tags with text:p """
    paragraphs = soup.find_all("p")

    for p_tag in paragraphs:
        p_tag.name = 'text:p'
    return soup


def parse_italic(soup):
    """ Replace i tags with text:span with autmotatic style """
    italic_tags = soup.find_all("em")
    for i_tag in italic_tags:
        i_tag.name = 'text:span'
        i_tag.attrs['text:style-name'] = "ITALIC"
    return soup


def parse_strong(soup):
    """ Replace strong tags with text:span with autmotatic style """
    strong_tags = soup.find_all("strong")
    for s_tag in strong_tags:
        s_tag.name = 'text:span'
        s_tag.attrs['text:style-name'] = "BOLD"
    return soup


def parse_underline(soup):
    """ Replace u tags with text:span with automatic style """
    u_tags = soup.find_all("u")
    for u_tag in u_tags:
        u_tag.name = 'text:span'
        u_tag.attrs['text:style-name'] = "UNDERLINE"
    return soup


def fix_li(soup, tag):
    tag.name = 'text:list-item'
    contents = ''
    for e in tag.contents:
        # get tag content formatted (keep nested tags)
        contents = f'{contents}{e}'
    tag.string = ''
    content = soup.new_tag('text:p')
    content.attrs['text:style-name'] = "Standard"
    content.append(BeautifulSoup(contents, 'html.parser'))
    tag.append(content)


def parse_ul(soup):
    """ Replace ul / li tags text:list and text:list-item """
    ul_tags = soup.find_all("ul")

    for ul_tag in ul_tags:
        ul_tag.name = 'text:list'
        ul_tag.attrs['xml:id'] = f'list{str(random.randint(100000000000000000, 900000000000000000))}'
        ul_tag.attrs['text:style-name'] = "L1"
        li_tags = ul_tag.findChildren(recursive=False)

        for li in li_tags:
            fix_li(soup, li)

    return soup


def parse_ol(soup):
    """ Replace ol / li tags text:list and text:list-item """
    ol_tags = soup.find_all("ol")
    for ol_tag in ol_tags:
        ol_tag.name = 'text:list'
        ol_tag.attrs['xml:id'] = f'list{str(random.randint(100000000000000000, 900000000000000000))}'
        ol_tag.attrs['text:style-name'] = "L2"
        ol_tag.attrs['text:level'] = "1"
        li_tags = ol_tag.findChildren(recursive=False)

        for li in li_tags:
            fix_li(soup, li)
    return soup


def parse_a(soup):
    # replace a
    a_tags = soup.find_all("a")
    for a_tag in a_tags:
        a_tag.name = 'text:a'
        new_attrs = {
            'xlink:type': 'simple',
            'xlink:href': a_tag.attrs['href']
        }
        a_tag.attrs = new_attrs

    return soup


def parse_h(soup):
    # replace h*
    h_tags = soup.find_all(re.compile("^h[0-3]"))
    for h_tag in h_tags:
        num = h_tag.name[1]
        h_tag.name = 'text:h'
        new_attrs = {
            'text:outline-level': num
        }
        h_tag.attrs = new_attrs
    return soup


def parse_br(soup):
    # replace br
    br_tags = soup.find_all("br")
    for br_tag in br_tags:
        br_tag.name = 'text:line-break'
    return soup


@register.filter()
def from_html(value, is_safe=True):
    """ Convert HTML from rte fields to odt compatible format """
    soup = BeautifulSoup(value, "html.parser")
    soup = parse_p(soup)
    soup = parse_strong(soup)
    soup = parse_italic(soup)
    soup = parse_underline(soup)
    soup = parse_ul(soup)
    soup = parse_ol(soup)
    soup = parse_a(soup)
    soup = parse_h(soup)
    soup = parse_br(soup)
    return mark_safe(str(soup))


class ImageLoaderNodeURL(template.Node):
    def __init__(self, url, data=None, width=None, height=None, request="GET"):
        # saves the passed obj parameter for later use
        # this is a template.Variable, because that way it can be resolved
        # against the current context in the render method
        self.url = url
        self.data = data
        self.width = width
        self.height = height
        self.request = request

    def render(self, context):
        self.get_value_context(context)
        name = secrets.token_hex(15)
        response = self.get_content_url()
        if not response:
            return ""
        width, height = resize(response.content, self.width, self.height, odt=True)
        context.setdefault('images', {})
        context['images'].update({name: {'content': response.content}})
        return mark_safe(ODT_IMAGE.format(name, width, height))

    def get_value_context(self, context):
        self.url = self.url.resolve(context)
        if self.request != "GET":
            self.request = self.request.resolve(context)
        if self.width:
            self.width = self.width.resolve(context)
        if self.height:
            self.height = self.height.resolve(context)

    def get_content_url(self):
        try:
            response = getattr(requests, self.request.lower())(self.url, data=self.data)
        except requests.exceptions.ConnectionError:
            logger.warning("Connection Error, check the url given")
            return
        except AttributeError:
            logger.warning("Type of request specified not allowed")
            return
        if response.status_code != 200:
            logger.warning("The picture is not accessible (Error: %s)" % response.status_code)
            return
        return response


@register.tag
def image_url_loader(parser, token):
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
    tag_name, args, kwargs = parse_tag(token, parser)
    usage = '{{% {tag_name} [url] width="5000" height="5000" ' \
            'request="GET" data="{{"data": "example"}}"%}}'.format(tag_name=tag_name)
    if len(args) > 1 or not all(key in ['width', 'height', 'request', 'data'] for key in kwargs.keys()):
        raise template.TemplateSyntaxError("Usage: %s" % usage)
    return ImageLoaderNodeURL(*args, **kwargs)


class ImageLoaderNode(template.Node):
    def __init__(self, object, width=None, height=None):
        # saves the passed obj parameter for later use
        # this is a template.Variable, because that way it can be resolved
        # against the current context in the render method
        self.object = object
        self.width = width
        self.height = height

    def render(self, context):
        # Evaluate the arguments in the current context
        # TODO: Move content with the binary of the picture directly in self.object : context[image] = Binary
        self.get_value_context(context)
        if isinstance(self.object, FilterExpression) or not self.object.get('content') \
                or not isinstance(self.object.get('content'), bytes):
            # if the object is still a FilterExpression, it means that resolve didn't work
            logger.warning("{object} is not a valid picture".format(object=self.object))
            return ""
        name = secrets.token_hex(15)
        width, height = resize(self.object.get('content'), self.width, self.height, odt=True)
        context.setdefault('images', {})
        context['images'].update({name: self.object})
        return mark_safe(ODT_IMAGE.format(name, width, height))

    def get_value_context(self, context):
        object = self.object.resolve(context)
        if object:
            self.object = object
        if self.width:
            self.width = self.width.resolve(context)
        if self.height:
            self.height = self.height.resolve(context)


@register.tag
def image_loader(parser, token):
    """
    Replace a tag by an image you specified.
    You must add an entry to the ``context`` var that is a dict with at least a ``content`` key
    whose value is a byte object. You can also specify ``width`` and ``height``, otherwise it will
    automatically resize your image.
    """
    tag_name, args, kwargs = parse_tag(token, parser)
    usage = '{{% {tag_name} [image] width="5000" height="5000" %}}'.format(tag_name=tag_name)
    if len(args) > 1 or set(kwargs.keys()) != {'width', 'height'} and len(kwargs.keys()) != 0:
        raise template.TemplateSyntaxError("Usage: %s" % usage)
    return ImageLoaderNode(*args, **kwargs)
