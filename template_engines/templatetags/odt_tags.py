import secrets
import random
import re
import requests

from bs4 import BeautifulSoup
from django import template
from django.utils.safestring import mark_safe

from template_engines.backends.utils_odt import ODT_IMAGE
from .utils import resize

register = template.Library()


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
        name = secrets.token_hex(15)
        if self.request.lower() == 'get':
            response = requests.get(self.url, data=self.data)
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
        width, height = resize(response.content, self.width, self.height, odt=True)
        if context.get('images'):
            context['images'].update({name: {'name': name, 'content': response.content}})
        else:
            context['images'] = {name: {'name': name, 'content': response.content}}
        return mark_safe(ODT_IMAGE.format(name, width, height))


def check_keys_odt_image_url_loader(key, value):
    if not key:
        raise template.TemplateSyntaxError(
            "You have to put the name of the key in the template"
        )
    if key not in ['url', 'width', 'height', 'request', 'data']:
        raise template.TemplateSyntaxError(
            "%s : this argument doesn't exist" % key
        )
    if not value:
        raise template.TemplateSyntaxError(
            "%s's value not given" % key
        )


def check_name_url_odt_image_url_loader(tokens):
    if not tokens.get('url'):
        raise template.TemplateSyntaxError(
            "An url has to be given"
        )


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

    #  token.split_contents()[0] is odt_image_loader
    contents = token.split_contents()[1:]
    tokens = {}
    for var in contents:
        var = var.replace('&quot;', '"')
        c1 = re.compile(r'([^"=]+)?([=]?"([^"]+)"|$)')
        match = c1.match(var)
        key = match.group(1)
        value = match.group(3)
        check_keys_odt_image_url_loader(key, value)
        tokens.update({key: value})
    check_name_url_odt_image_url_loader(tokens)
    return ImageLoaderNodeURL(**tokens)


class ImageLoaderNode(template.Node):
    def __init__(self, object, width=None, height=None):
        # saves the passed obj parameter for later use
        # this is a template.Variable, because that way it can be resolved
        # against the current context in the render method
        self.image_name = object
        self.width = width
        self.height = height

    def render(self, context):
        self.image = context[self.image_name]
        name = secrets.token_hex(15)
        self.image['name'] = name
        width, height = resize(self.image.get('content'), self.width, self.height, odt=True)
        if context.get('images'):
            context['images'].update({name: self.image})
        else:
            context['images'] = {name: self.image}
        return mark_safe(ODT_IMAGE.format(name, width, height))


def check_keys_odt_image_loader(key, value):
    if not key:
        raise template.TemplateSyntaxError(
            "You have to put the name of the key in the template"
        )
    if key not in ['object', 'width', 'height']:
        raise template.TemplateSyntaxError(
            "%s : this argument doesn't exist" % key
        )
    if not value:
        raise template.TemplateSyntaxError(
            "%s's value not given" % key
        )


def check_object_odt_image_loader(tokens):
    if not tokens.get('object'):
        raise template.TemplateSyntaxError(
            "An object has to be given"
        )


@register.tag
def image_loader(parser, token):
    """
    Replace a tag by an image you specified.
    You must add an entry to the ``context`` var that is a dict with at least a ``content`` key
    whose value is a byte object. You can also specify ``width`` and ``height``, otherwise it will
    automatically resize your image.
    """
    #  token.split_contents()[0] is odt_image_loader
    contents = token.split_contents()[1:]
    tokens = {}
    for var in contents:
        var = var.replace('&quot;', '"')
        c1 = re.compile(r'([^"=]+)?([=]?"([^"]+)"|$)')
        match = c1.match(var)
        key = match.group(1)
        value = match.group(3)
        check_keys_odt_image_loader(key, value)
        tokens.update({key: value})
    check_object_odt_image_loader(tokens)
    return ImageLoaderNode(**tokens)
