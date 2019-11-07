"""
Contains all generic functions that can be used to build test_backends.
"""
import io
import re
from tempfile import NamedTemporaryFile
from zipfile import ZipFile

from django.core.files.storage import default_storage


def modify_content_document(file_path, xml_path, rendered):
    """
    Modify a libreoffice document (docx and odt only for the moment).

    :param file_path: the path of the zip file.
    :type file_path: str

    :param xml_path: path to the xml representation of the document.
    :type xml_path: str

    :param rendered: content to put in the xml representation of the document.
    :type rendered: str

    :returns: the modified file as a byte object.
    """
    temp_file = NamedTemporaryFile()

    template_buffer = io.BytesIO(default_storage.open(file_path, 'rb').read())
    with ZipFile(template_buffer, 'r') as read_zip_file:
        info_list = read_zip_file.infolist()
        with ZipFile(temp_file.name, 'w') as write_zip_file:
            for item in info_list:
                if item.filename == xml_path:
                    write_zip_file.writestr(item, rendered)
                else:
                    write_zip_file.writestr(item, read_zip_file.read(item.filename))

    with open(temp_file.name, 'rb') as read_file:
        return read_file.read()


def clean_tags(content):
    template_tag = re.compile(r'\{\{([^\}]+)\}\}|\{\%([^\%]+)\%\}')
    bad_content = re.compile(r'\<[^\>]*\>|\«[^\»]\»|\“[^\”]\”')
    return template_tag.sub(
        lambda e: bad_content.sub('', e.group(0)),
        content,
    )
