import io
import zipfile
from os.path import join

from django.core.files.storage import default_storage
from django.template import Template
from django.template.backends.base import BaseEngine
from django.template.loader import TemplateDoesNotExist
from django.utils.functional import cached_property

from .utils import clean_tags


class AbstractTemplate:
    """
    Gives the architecture of a basic template.

    ``clean`` and ``render`` must be implemented.
    """

    def __init__(self, template):
        self.template = template

    def clean(self, data):
        """
        Method for cleaning rendered data.
        """
        raise NotImplementedError()

    def render(self, context=None, request=None):
        """
        Fills a template with the context obtained by combining the `context` and` request`
        parameters and returns a file as a byte object.
        """
        raise NotImplementedError()


class ZipAbstractEngine(BaseEngine):
    """
    Gives the architecture of a basic zip base template engine.

    Can be specified:

    * ``app_dirname``, the folder name which contains the templates in application directories,
    * ``sub_dirname``, the folder name of the subdirectory in the templates directory,
    * ``template_class``, your own template class with a ``render`` method,
    * ``zip_root_file``, the file to fill.
    """
    app_dirname = None
    sub_dirname = None
    template_class = None
    zip_root_file = None

    def __init__(self, params):
        params = params.copy()
        self.options = params.pop('OPTIONS')
        super().__init__(params)

    def get_template_content(self, filename):
        """
        Returns the contents of a template before modification, as a string.
        """
        try:
            template_buffer = io.BytesIO(default_storage.open(filename, 'rb').read())
            with zipfile.ZipFile(template_buffer, 'r') as zip_file:
                b_content = zip_file.read(self.zip_root_file)
                return b_content.decode()
        except KeyError:
            raise TemplateDoesNotExist('Bad format.')

    @cached_property
    def template_dirs(self):
        t_dirs = super().template_dirs
        if self.sub_dirname:
            t_dirs += tuple([join(p, self.sub_dirname) for p in t_dirs])
        return t_dirs

    def from_string(self, template_code, **kwargs):
        return self.template_class(Template(template_code), **kwargs)

    def get_template_path(self, filename):
        """
        Check if a template named ``template_name`` can be found in a list of directories. Returns
        the path if the file exists or raises ``TemplateDoesNotExist`` otherwise.
        """
        if default_storage.exists(filename):
            return filename
        for directory in self.template_dirs:
            abstract_path = default_storage.generate_filename(join(directory, filename))
            if default_storage.exists(abstract_path):
                return abstract_path
        raise TemplateDoesNotExist(f'Unknown: {filename}')

    def clean_content(self, content):
        return clean_tags(content)

    def get_template(self, template_name):
        template_path = self.get_template_path(template_name)
        content = self.get_template_content(template_path)
        content = self.clean_content(content)
        return self.from_string(content, template_path=template_path)
