from bs4 import BeautifulSoup
import os
from tempfile import NamedTemporaryFile
from zipfile import ZipFile

ODT_IMAGE = (
    '<draw:frame draw:name="{0}" svg:width="{1}" svg:height="{2}" text:anchor-type="paragraph" draw:z-index="0" '
    'text:anchor-type="paragraph">'
    '<draw:image xlink:href="Pictures/{0}" xlink:show="embed" xlink:actuate="onLoad">'
    '</draw:image></draw:frame>'
)


def add_image_in_odt_template(bfile, image, name):
    """
    Makes an image available for a odt document.

    :param bfile: the odt document.
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
                if item.filename == 'META-INF/manifest.xml':
                    doc_relationships = read_zip_file.read(item.filename)
                    soup = BeautifulSoup(doc_relationships, features='xml')
                    manifest = soup.find('manifest:manifest')
                    file_entry = soup.new_tag('manifest:file-entry')
                    _, ext = os.path.splitext(name)
                    attributes_file_entry = {
                        'manifest:full-path': 'Pictures/{}'.format(name),
                        'manifest:media-type': 'image/{}'.format(ext)
                    }
                    file_entry.attrs = attributes_file_entry
                    manifest.append(file_entry)
                    write_zip_file.writestr(item.filename, str(soup))
                else:
                    write_zip_file.writestr(item, read_zip_file.read(item.filename))

            # Add the image in the word/media folder
            temp_image = NamedTemporaryFile()
            with open(temp_image.name, 'wb') as writer:
                writer.write(image.get('content'))
            write_zip_file.write(
                temp_image.name,
                arcname='Pictures/{}'.format(name))

    with open(temp_doc.name, 'rb') as read_file:
        return read_file.read()
