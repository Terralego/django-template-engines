import base64
from random import randint

from bs4 import BeautifulSoup
from django import template
from django.utils.safestring import mark_safe

from template_engines.odt_helpers import ODT_IMAGE
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


def parse_p(soup):
    """ Replace p tags with text:p """
    paragraphs = soup.find_all("p")

    for p_tag in paragraphs:
        p_tag.name = 'text:p'
    return soup


def parse_italic(soup):
    """ Replace i tags with text:span with autmotatic style """
    italic_tags = soup.find_all("i")
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


def parse_ul(soup):
    """ Replace ul / li tags text:list and text:list-item """
    ul_tags = soup.find_all("ul")

    for ul_tag in ul_tags:
        ul_tag.name = 'text:list'
        ul_tag.attrs['xml:id'] = f'list{str(randint(100000000000000000, 900000000000000000))}'
        ul_tag.attrs['text:style-name'] = "L1"
        li_tags = ul_tag.findChildren(recursive=False)

        for li in li_tags:
            li.name = 'text:list-item'
            # need to wrap li content with text:p tag
            contents = ''
            for e in li.contents:
                # get tag content formatted (keep nested tags)
                contents = f'{contents}{e}'
            li.string = ''
            content = soup.new_tag('text:p')
            content.attrs['text:style-name'] = "Standard"
            content.append(BeautifulSoup(contents, 'html.parser'))
            li.append(content)

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
    soup = parse_a(soup)
    soup = parse_br(soup)
    return mark_safe(str(soup))
