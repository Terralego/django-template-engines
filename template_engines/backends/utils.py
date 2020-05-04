"""
Contains all generic functions that can be used to build test_backends.
"""
from bs4 import BeautifulSoup
import io
import os
import re
from tempfile import NamedTemporaryFile
from zipfile import ZipFile

from django.core.files.storage import default_storage


def get_rendered_by_xml(xml_paths, soup):
    dict_xml = {}
    for xml_path in xml_paths:
        name = os.path.splitext(xml_path)[0]
        merged = soup.find('{}-merged'.format(name.replace('/', '-')))
        dict_xml[xml_path] = merged.contents[0] if merged.contents else ''
    return dict_xml


def modify_content_document(file_path, xml_paths, soup):
    """
    Modify a libreoffice document (docx and odt only for the moment).

    :param file_path: the path of the zip file.
    :type file_path: str

    :param xml_paths: path to the xml representation of the document.
    :type xml_paths: List[str]

    :param rendered: content to put in the xml representation of the document.
    :type rendered: str

    :returns: the modified file as a byte object.
    """

    temp_file = NamedTemporaryFile()
    dict_xml_render = get_rendered_by_xml(xml_paths, soup)
    with default_storage.open(file_path, 'rb') as template_file:
        template_buffer = io.BytesIO(template_file.read())

    with ZipFile(template_buffer, 'r') as read_zip_file:
        info_list = read_zip_file.infolist()

        with ZipFile(temp_file.name, 'w') as write_zip_file:
            for item in info_list:
                if item.filename in xml_paths:
                    version = BeautifulSoup(read_zip_file.read(item.filename).decode(), 'html.parser')
                    version.findChild().decompose()
                    version.append(dict_xml_render[item.filename])
                    write_zip_file.writestr(item, str(version))
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
