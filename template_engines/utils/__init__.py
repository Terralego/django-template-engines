import io
import logging
import os
import re
import requests
from PIL import Image
from tempfile import NamedTemporaryFile
from zipfile import ZipFile

from bs4 import BeautifulSoup
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)


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


def get_content_url(url, type_request, data):
    try:
        response = getattr(requests, type_request.lower())(url, data=data)
    except requests.exceptions.ConnectionError:
        logger.warning("Connection Error, check the url given")
        return
    except AttributeError:
        logger.warning("Type of request specified not allowed")
        return
    if response.status_code != 200:
        logger.warning("The picture is not accessible (Error: %s)" % response.status_code)
        return
    return response


def get_extension_picture(image):
    bimage = io.BytesIO(image)
    with Image.open(bimage) as img_reader:
        extension = img_reader.format.lower()
    return extension
