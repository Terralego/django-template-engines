"""
Contains all generic functions that can be used to build backends.
"""
from tempfile import NamedTemporaryFile
from zipfile import ZipFile


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
    with ZipFile(file_path, 'r') as read_zip_file:
        info_list = read_zip_file.infolist()
        with ZipFile(temp_file.name, 'w') as write_zip_file:
            for item in info_list:
                if item.filename != xml_path:
                    write_zip_file.writestr(item, read_zip_file.read(item.filename))
                else:
                    write_zip_file.writestr(item, rendered)
    with open(temp_file.name, 'rb') as read_file:
        return read_file.read()
