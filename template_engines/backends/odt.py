from bs4 import BeautifulSoup
from django.conf import settings
from django.template import Context
from django.template.context import make_context

from .abstract import AbstractTemplate, ZipAbstractEngine
from .utils import modify_content_document
from .utils_odt import add_image_in_odt_template


class OdtTemplate(AbstractTemplate):
    """
    Handles odt templates.
    Check http://docs.oasis-open.org/office/v1.2/os/OpenDocument-v1.2-os-part1.html#__RefHeading__1418974_253892949 for hints
    """

    def __init__(self, template, template_path=None):
        """
        :param template: the template to fill.
        :type template: django.template.Template

        :param template_path: path to the template.
        :type template_path: str
        """
        super().__init__(template)
        self.template_path = template_path

    def _get_automatic_style(self, soup, style_attrs=None, properties_attrs=None):
        # set params immutables
        if properties_attrs is None:
            properties_attrs = {}
        if style_attrs is None:
            style_attrs = {}

        # add bold style
        style = soup.new_tag('style:style')
        style.attrs = style_attrs

        style_properties = soup.new_tag('style:text-properties')
        style_properties.attrs = properties_attrs
        style.append(style_properties)
        return style

    def get_automatic_style_bold(self, soup):
        """ get style for italic """
        style_attrs = {
            "style:name": "BOLD",
            "style:family": "text"
        }
        text_prop_attrs = {
            "fo:font-weight": "bold",
            "style:font-weight-asian": "bold",
            "style:font-weight-complex": "bold",
        }
        return self._get_automatic_style(
            soup, style_attrs, text_prop_attrs
        )

    def get_automatic_style_italic(self, soup):
        """ get style for italic """
        style_attrs = {
            "style:name": "ITALIC",
            "style:family": "text"
        }
        text_prop_attrs = {"fo:font-style": "italic", }
        return self._get_automatic_style(
            soup, style_attrs, text_prop_attrs
        )

    def get_automatic_style_underline(self, soup):
        """ get style for underline """
        style_attrs = {
            "style:name": "UNDERLINE",
            "style:family": "text"
        }
        text_prop_attrs = {
            "style:text-underline-style": "solid",
            "style:text-underline-width": "auto",
            "style:text-underline-color": "font-color"
        }
        return self._get_automatic_style(
            soup, style_attrs, text_prop_attrs
        )

    def get_automatic_style_orderedlist(self, soup):
        """ get style for orderedlist """
        style = soup.new_tag('text:list-style')
        style_ol_attrs = {
            "style:name": "L2",
        }
        style.attrs = style_ol_attrs
        # Style of the number : 1.
        style_number = soup.new_tag('text:list-level-style-number')
        style_number.attrs = {"text:level": "1", "style:num-suffix": ".", "style:num-format": "1"}
        style.append(style_number)
        # Style of the alignment between each text
        style_list_properties = soup.new_tag('style:list-level-properties')
        style_list_properties.attrs = {"text:list-level-position-and-space-mode": "label-alignment"}
        style_number.append(style_list_properties)
        # Space between text and number : "listtab, nothing or space allowed
        style_alignment = soup.new_tag('style:list-level-label-alignment')
        style_alignment.attrs = {"text:label-followed-by": "space", "fo:text-indent": "0.435cm"}
        style_list_properties.append(style_alignment)
        return style

    def get_automatic_style_unorderedlist(self, soup):
        """ get style for unorderedlist """
        style = soup.new_tag('text:list-style')
        style_ul_attrs = {
            "style:name": "L1",
        }
        style.attrs = style_ul_attrs
        # Style of the number : 1.
        style_number = soup.new_tag('text:list-level-style-bullet')
        style_number.attrs = {"text:level": "1", "text:bullet-char": "•"}
        style.append(style_number)
        # Style of the alignment between each text
        style_list_properties = soup.new_tag('style:list-level-properties')
        style_list_properties.attrs = {"text:list-level-position-and-space-mode": "label-alignment"}
        style_number.append(style_list_properties)
        # Space between text and number : "listtab, nothing or space allowed
        style_alignment = soup.new_tag('style:list-level-label-alignment')
        style_alignment.attrs = {"text:label-followed-by": "space", "fo:text-indent": "0.635cm"}
        style_list_properties.append(style_alignment)
        return style

    def clean(self, soup):
        """ Add styles for html filters """

        # find automatic-styles tag
        automatic_styles = soup.find('office:automatic-styles')

        # add bold style
        style_bold = self.get_automatic_style_bold(soup)
        automatic_styles.append(style_bold)
        # add italic style
        style_bold = self.get_automatic_style_italic(soup)
        automatic_styles.append(style_bold)
        # add underline style
        style_underline = self.get_automatic_style_underline(soup)
        automatic_styles.append(style_underline)
        # add orderedline style
        style_orderedlist = self.get_automatic_style_orderedlist(soup)
        automatic_styles.append(style_orderedlist)
        # add unorderedline style
        style_unorderedlist = self.get_automatic_style_unorderedlist(soup)
        automatic_styles.append(style_unorderedlist)

        return soup

    def replace_inputs(self, soup):
        """ Replace all text:text-input to text-span """
        input_list = soup.find_all("text:text-input")

        for tag in input_list:
            contents = ''
            for e in tag.contents:
                # get tag content formatted (keep nested tags)
                contents = f'{contents}{e}'

            if BeautifulSoup(contents, 'html.parser').findChildren("text:p", recursive=False):
                tag.find_parent('text:p').insert_after(BeautifulSoup(contents, 'html.parser'))
            else:
                tag.find_parent('text:p').append(contents)
            tag.extract()
        return soup

    def render(self, context=None, request=None):
        context = make_context(context, request)
        rendered = self.template.render(Context(context))
        soup = BeautifulSoup(rendered, features='xml')
        soup = self.clean(soup)
        soup = self.replace_inputs(soup)
        odt_content = modify_content_document(self.template_path, 'content.xml', str(soup))
        for key, image in context.get('images', {}).items():
            odt_content = add_image_in_odt_template(odt_content, image, key)
        return odt_content


class OdtEngine(ZipAbstractEngine):
    """
    Odt template engine.

    By default, ``app_dirname`` is equal to 'templates' but you can change this value by adding an
    ``ODT_ENGINE_APP_DIRNAME`` setting in your settings.
    By default, ``sub_dirname`` is equal to 'odt' but you can change this value by adding an
    ``ODT_ENGINE_SUB_DIRNAME`` setting in your settings.
    By default, ``OdtTemplate`` is used as template_class.
    """
    sub_dirname = getattr(settings, 'ODT_ENGINE_SUB_DIRNAME', 'odt')
    app_dirname = getattr(settings, 'ODT_ENGINE_APP_DIRNAME', 'templates')
    template_class = OdtTemplate
    zip_root_file = 'content.xml'

    def __init__(self, params):
        params['OPTIONS'].setdefault('builtins', [])
        params['OPTIONS']['builtins'].extend(['template_engines.templatetags.odt_tags'])
        super().__init__(params)
