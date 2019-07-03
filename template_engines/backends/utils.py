"""
Contains all generic functions that can be used to build backends.
"""
from tempfile import NamedTemporaryFile
from zipfile import ZipFile


def modify_zip_file(file_path, handler, rendered):
    """
    Modify a zip file.
    :param file_path: the path of the zip file.
    :type file_path: str

    :param handler: you must write a function that takes, the result of ZipFile(..., 'r') as \
read_zip_file ; the result of ZipFile(..., 'w') as write_zip_file ; item an element of \
read_zip_file.infolist() and kwargs. This function will modify the file at your convinience.
    :type handler: function

    :param kwargs: some things that your handler may need.

    :returns: your modified zip file as a byte object.

    .. note :: this handler makes a copy
       ::

            def copy_handler(read_zip_file, write_zip_file, item, **kwargs):
                write_zip_file.writestr(item, read_zip_file.read(item.filename))
    """
    temp_file = NamedTemporaryFile()
    with ZipFile(file_path, 'r') as read_zip_file:
        info_list = read_zip_file.infolist()
        with ZipFile(temp_file.name, 'w') as write_zip_file:
            for item in info_list:
                handler(read_zip_file, write_zip_file, item, rendered)
    with open(temp_file.name, 'rb') as read_file:
        return read_file.read()
