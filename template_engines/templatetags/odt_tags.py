from xml.dom.minidom import parseString

from bs4 import BeautifulSoup
from django import template

from template_engines.odt_helpers import transform_map, \
    node_to_string, get_style_by_name, traverse_preformatted, ODT_IMAGE

from base64 import b64encode

from django import template
from django.utils.safestring import mark_safe

from .utils import resize

register = template.Library()



@register.filter()
def html_convert(html_text):
    """ Convert a html text into a ODT formatted text """

    # cache styles searching
    styles_cache = {}

    encoded = html_text.encode('ascii', 'xmlcharrefreplace')
    if isinstance(encoded, bytes):
        # In PY3 bytes-like object needs convert to str
        encoded = encoded.decode('ascii')
    soup = BeautifulSoup(encoded)
    xml_object = parseString('<html>%s</html>' % soup.body.next)

    # Transform HTML tags as specified in transform_map
    # Some tags may require extra attributes in ODT.
    # Additional attributes are indicated in the 'attributes' property

    for tag in transform_map:
        html_nodes = xml_object.getElementsByTagName(tag)
        for html_node in html_nodes:
            odt_node = xml_object.createElement(transform_map[tag]['replace_with'])

            # Transfer child nodes
            if html_node.hasChildNodes():
                # We can't directly insert text into a text:list-item element.
                # The content of the item most be wrapped inside a container
                # like text:p. When there's not a double linebreak separating
                # list elements, markdown2 creates <li> elements without wraping
                # their contents inside a container. Here we automatically create
                # the container if one was not created by markdown2.
                if tag == 'li' and html_node.childNodes[0].localName != 'p':
                    container = xml_object.createElement('text:p')
                    odt_node.appendChild(container)

                elif tag == 'code':
                    traverse_preformatted(html_node, xml_object)
                    container = odt_node

                else:
                    container = odt_node

                for child_node in html_node.childNodes:
                    container.appendChild(child_node.cloneNode(True))

            # Add style-attributes defined in transform_map
            if 'style_attributes' in transform_map[tag]:
                for k, v in transform_map[tag]['style_attributes'].items():
                    odt_node.setAttribute('text:%s' % k, v)

            # Add defined attributes
            if 'attributes' in transform_map[tag]:
                for k, v in transform_map[tag]['attributes'].items():
                    odt_node.setAttribute(k, v)

                # copy original href attribute in <a> tag
                if tag == 'a' and html_node.hasAttribute('href'):
                    odt_node.setAttribute('xlink:href',
                                          html_node.getAttribute('href'))

            # Does the node need to create an style?
            if 'style' in transform_map[tag]:
                name = transform_map[tag]['style']['name']
                if name not in styles_cache:
                    style_node = get_style_by_name(self.content, name)

                    if style_node is None:
                        # Create and cache the style node
                        style_node = self.insert_style_in_content(
                            name, transform_map[tag]['style'].get('attributes', None),
                            **transform_map[tag]['style']['properties'])
                        styles_cache[name] = style_node

            html_node.parentNode.replaceChild(odt_node, html_node)

    odt_text = ''.join(node_as_str for node_as_str in map(node_to_string,
                                                          xml_object.getElementsByTagName('html')[0].childNodes))

    return odt_text


@register.simple_tag
def image_loader(image):
    """
    Replace a tag by an image you specified.
    You must add an entry to the ``context`` var that is a dict with at least a ``content`` key
    whose value is a byte object. You can also specify ``width`` and ``height``, otherwise it will
    automatically resize your image.
    """
    width = image.get('width')
    height = image.get('height')
    content = image.get('content')

    width, height = resize(content, width, height)

    return mark_safe(ODT_IMAGE.format(width, height, b64encode(content).decode()))  # nosec
