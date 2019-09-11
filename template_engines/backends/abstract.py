from os.path import join

from django.core.files.storage import default_storage
from django.template import Template
from django.template.backends.base import BaseEngine
from django.template.loader import TemplateDoesNotExist
from django.utils.functional import cached_property
from magic import from_buffer


class AbstractTemplate:
    """
    Gives the architecture of a basic template and one implemented method:
    ``clean``.

    ``render`` must be implemented.
    """

    def __init__(self, template):
        self.template = template

    def clean(self, data):
        """
        Method for cleaning rendered data. For this to work, you must implement methods whose names
        start with ``clean_``.
        """
        unit_clean_method_names = list(filter(lambda e: e.startswith('clean_'), dir(self)))
        unit_clean_methods = list(map(lambda e: getattr(self, e), unit_clean_method_names))
        for clean_method in unit_clean_methods:
            data = clean_method(data)
        return data

    def render(self, context=None, request=None):
        """
        Fills a template with the context obtained by combining the `context` and` request`
        parameters and returns a file as a byte object.
        """
        raise NotImplementedError()


class AbstractEngine(BaseEngine):
    """
    Gives the architecture of a basic template engine and two implemented methods:
    ``get_template_path`` and ``from_string``.

    Can be specified:

    * ``app_dirname``, the folder name which contains the templates in application directories,
    * ``sub_dirname``, the folder name of the subdirectory in the templates directory,
    * ``template_class``, your own template class with a ``render`` method.

    ``get_template`` must be implemented.
    """
    app_dirname = None
    sub_dirname = None
    template_class = None
    mime_type = None

    def __init__(self, params):
        params = params.copy()
        self.options = params.pop('OPTIONS')
        super().__init__(params)

    @cached_property
    def template_dirs(self):
        t_dirs = super().template_dirs
        if self.sub_dirname:
            t_dirs += tuple([join(p, self.sub_dirname) for p in t_dirs])
        return t_dirs

    def from_string(self, template_code, **kwargs):
        return self.template_class(Template(template_code), **kwargs)

    def check_mime_type(self, path):
        template = default_storage.open(path, 'rb').read()
        fmime_type = from_buffer(template, mime=True)
        if fmime_type != self.mime_type:
            raise TemplateDoesNotExist('Bad template.')

    def get_template_path(self, filename):
        """
        Check if a template named ``template_name`` can be found in a list of directories. Returns
        the path if the file exists or raises ``TemplateDoesNotExist`` otherwise.
        """
        if default_storage.exists(filename):
            self.check_mime_type(filename)
            return filename
        for directory in self.template_dirs:
            abstract_path = default_storage.generate_filename(join(directory, filename))
            if default_storage.exists(abstract_path):
                self.check_mime_type(abstract_path)
                return abstract_path
        raise TemplateDoesNotExist(f'Unknown: {filename}')

    def get_template(self, template_name):
        raise NotImplementedError()
