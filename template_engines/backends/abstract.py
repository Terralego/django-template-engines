from glob import glob
from os.path import isdir, isfile, join

from django.template import Template
from django.template.backends.base import BaseEngine
from django.template.loader import TemplateDoesNotExist
from django.utils.functional import cached_property
from magic import from_file


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
            t_dirs += tuple([join(p, self.sub_dirname)
                             for p in t_dirs
                             if isdir(join(p, self.sub_dirname))])
        return t_dirs

    def from_string(self, template_code, **kwargs):
        return self.template_class(Template(template_code), **kwargs)

    def check_mime_type(self, path):
        fmime_type = from_file(path, mime=True)
        if fmime_type != self.mime_type:
            raise TemplateDoesNotExist('Bad template.')

    def get_template_path(self, template_name):
        """
        Check if a template named ``template_name`` can be found in a list of directories. Returns
        the path if the file exists or raises ``TemplateDoesNotExist`` otherwise.
        """
        if isfile(template_name):
            self.check_mime_type(template_name)
            return template_name
        template_path = None
        for directory in self.template_dirs:
            abstract_path = join(directory, template_name)
            path = glob(abstract_path)
            if path:
                template_path = path[0]
                break
        if template_path is None:
            raise TemplateDoesNotExist(f'Unknown: {template_name}')
        self.check_mime_type(template_path)
        return template_path

    def get_template(self, template_name):
        raise NotImplementedError()
