"""
Contains all generic functions that can be used to build test_backends.
"""
import io
import re
from tempfile import NamedTemporaryFile
from zipfile import ZipFile

from django.core.files.storage import default_storage

DOCX_RELATIONSHIP = (
    '<Relationship Id="{0}" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
    + 'relationships/image" Target="media/{0}"/></Relationships>')


def modify_libreoffice_doc(file_path, xml_path, rendered):
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


def add_image_in_docx_template(bfile, image):
    """
    Makes an image available for a docx document.

    :param bfile: the docx document.
    :type bfile: bytes

    :param image: a dictionary with at least two entries: the image's name and the image's content.
    :type image: dict
    """
    temp_file = NamedTemporaryFile()
    with open(temp_file.name, 'wb') as writer:
        writer.write(bfile)

    temp_doc = NamedTemporaryFile()
    with ZipFile(temp_file.name, 'r') as read_zip_file:
        with ZipFile(temp_doc.name, 'w') as write_zip_file:
            # Add a relationship tag to word/_rels/document.xml.rels
            for item in read_zip_file.infolist():
                if item.filename == 'word/_rels/document.xml.rels':
                    doc_relationships = read_zip_file.read(item.filename).decode()
                    doc_relationships = re.sub(
                        '</Relationships>',
                        DOCX_RELATIONSHIP.format(image.get('name')),
                        doc_relationships)
                    write_zip_file.writestr(item.filename, doc_relationships)
                else:
                    write_zip_file.writestr(item, read_zip_file.read(item.filename))

            # Add the image in the word/media folder
            temp_image = NamedTemporaryFile()
            with open(temp_image.name, 'wb') as writer:
                writer.write(image.get('content'))
            write_zip_file.write(
                temp_image.name,
                arcname='word/media/{}'.format(image.get('name')))

    with open(temp_doc.name, 'rb') as read_file:
        return read_file.read()


def clean_tags(content):
    template_tag = re.compile(r'\{\{([^\}]+)\}\}|\{\%([^\%]+)\%\}')
    bad_content = re.compile(r'\<[^\>]*\>|\«[^\»]\»|\“[^\”]\”')
    return template_tag.sub(
        lambda e: bad_content.sub('', e.group(0)),
        content,
    )
