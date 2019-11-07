import re
from tempfile import NamedTemporaryFile
from zipfile import ZipFile


DOCX_RELATIONSHIP = (
    '<Relationship Id="{0}" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
    + 'relationships/image" Target="media/{0}"/></Relationships>')


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
        info_list = read_zip_file.infolist()
        with ZipFile(temp_doc.name, 'w') as write_zip_file:
            # Add a relationship tag to word/_rels/document.xml.rels
            for item in info_list:
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
