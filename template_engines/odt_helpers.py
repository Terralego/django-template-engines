from random import randint
import re

ODT_IMAGE = (
        '<draw:frame draw:name="img1" svg:width="{0}" svg:height="{1}">'
        + '<draw:image xlink:type="simple" xlink:show="embed" xlink:actuate="onLoad">'
        + '<office:binary-data>{2}</office:binary-data>'
        + '</draw:image></draw:frame>'
)

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
            'xml:id': 'list' + str(randint(100000000000000000, 900000000000000000))
        }
    },

    'ol': {
        'replace_with': 'text:list',
        'attributes': {
            'xml:id': 'list' + str(randint(100000000000000000, 900000000000000000))
        }
    },

    'li': {
        'replace_with': 'text:list-item'
    },

    'br': {
        'replace_with': 'text:line-break'
    },
}


def get_style_by_name(content, style_name):
    """
        Search in <office:automatic-styles> for style_name.
        Return None if style_name is not found. Otherwise
        return the style node
    """

    auto_styles = content.getElementsByTagName(
        'office:automatic-styles')[0]

    if not auto_styles.hasChildNodes():
        return None

    for style_node in auto_styles.childNodes:
        if style_node.hasAttribute('style:name') and \
                (style_node.getAttribute('style:name') == style_name):
            return style_node

    return None


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


ODT_IMAGE = (
        '<draw:frame draw:name="img1" svg:width="{0}" svg:height="{1}">'
        + '<draw:image xlink:type="simple" xlink:show="embed" xlink:actuate="onLoad">'
        + '<office:binary-data>{2}</office:binary-data>'
        + '</draw:image></draw:frame>'
)
