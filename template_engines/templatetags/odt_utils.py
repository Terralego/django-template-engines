import re
from xml.dom.minidom import parseString

from django import template
from markdown_map import transform_map

register = template.Library()

common_styles = {
    'italic': {
        'replace_with': 'text:span',
        'style_attributes': {
            'style-name': 'markdown_italic'
        },

        'style': {
            'name': 'markdown_italic',
            'properties': {
                'fo:font-style': 'italic',
                'style:font-style-asian': 'italic',
                'style:font-style-complex': 'italic'
            }
        }
    },

    'strong': {
        'replace_with': 'text:span',
        'style_attributes': {
            'style-name': 'markdown_bold'
        },

        'style': {
            'name': 'markdown_bold',
            'properties': {
                'fo:font-weight': 'bold',
                'style:font-weight-asian': 'bold',
                'style:font-weight-complex': 'bold'
            }
        }
    },

    'p': {
        'replace_with': 'text:p',
        'style_attributes': {
            'style-name': 'Standard'
        }
    }
}

transform_map = {
    'a': {
        'replace_with': 'text:a',
        'attributes': {
            'xlink:type': 'simple',
            'xlink:href': ''
        }
    },

    'p': common_styles['p'],
    'strong': common_styles['strong'],
    'em': common_styles['italic'],
    'b': common_styles['strong'],
    'i': common_styles['italic'],

    # Heading Styles (Use styles defined in the document)
    'h1': {
        'replace_with': 'text:p',
        'style_attributes': {
            'style-name': 'Heading_20_1'
        }
    },

    'h2': {
        'replace_with': 'text:p',
        'style_attributes': {
            'style-name': 'Heading_20_2'
        }
    },

    'h3': {
        'replace_with': 'text:p',
        'style_attributes': {
            'style-name': 'Heading_20_3'
        }
    },

    'h4': {
        'replace_with': 'text:p',
        'style_attributes': {
            'style-name': 'Heading_20_4'
        }
    },

    'pre': {
        'replace_with': 'text:p',
        'style_attributes': {
            'style-name': 'Preformatted_20_Text'
        }
    },

    'code': {
        'replace_with': 'text:span',
        'style_attributes': {
            'style-name': 'Preformatted_20_Text'
        }
    },

    'ul': {
        'replace_with': 'text:list',
        'attributes': {
            'xml:id': 'list' + str(randint(100000000000000000,900000000000000000))
        }
    },

    'ol': {
        'replace_with': 'text:list',
        'attributes': {
            'xml:id': 'list' + str(randint(100000000000000000,900000000000000000))
        }
    },

    'li': {
        'replace_with': 'text:list-item'
    },

    'br': {
        'replace_with': 'text:line-break'
    },
}

def node_to_string(node):
    return node.toxml()


def traverse_preformatted(node, xml_object):
    if node.hasChildNodes():
        for n in node.childNodes:
            traverse_preformatted(n)
    else:
        container = xml_object.createElement('text:span')
        for text in re.split('(\n)', node.nodeValue.lstrip('\n')):
            if text == '\n':
                container.appendChild(xml_object.createElement('text:line-break'))
            else:
                container.appendChild(xml_object.createTextNode(text))

        node.parentNode.replaceChild(container, node)


@register.filter()
def html_convert(self, html_text):
    """ Convert a html text into a ODT formatted text """

    # cache styles searching
    styles_cache = {}

    encoded = html_text.encode('ascii', 'xmlcharrefreplace')
    if isinstance(encoded, bytes):
        # In PY3 bytes-like object needs convert to str
        encoded = encoded.decode('ascii')
    xml_object = parseString('<html>%s</html>' % encoded)

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
                    style_node = self.get_style_by_name(name)

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
