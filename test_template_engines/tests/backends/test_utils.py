from io import BytesIO
from zipfile import ZipFile

from django.test import TestCase

from template_engines.backends.utils import modify_zip_file
from test_template_engines.tests.backends.backend_settings import ODT_TEMPLATE_PATH


def copy_handler(read_zip_file, write_zip_file, item, _rendered):
    write_zip_file.writestr(item, read_zip_file.read(item.filename))


class TestUtils(TestCase):

    def test_modify_zip_file_works(self):
        zip_copy = modify_zip_file(ODT_TEMPLATE_PATH, copy_handler, None)
        # Checks the return type
        self.assertIsInstance(zip_copy, bytes)

        buffer = BytesIO(zip_copy)
        with ZipFile(buffer, 'r') as buffer_zip_obj:
            with ZipFile(ODT_TEMPLATE_PATH, 'r') as odt_zip_obj:
                buffer_filename_list = list(map(lambda e: e.filename, buffer_zip_obj.infolist()))
                odt_filename_list = list(map(lambda e: e.filename, odt_zip_obj.infolist()))
                # Checks that the archive contains the same files
                self.assertEqual(buffer_filename_list, odt_filename_list)

                for filename in odt_filename_list:
                    # Checks that the files are dientical
                    self.assertEqual(buffer_zip_obj.read(filename), odt_zip_obj.read(filename))

    def test_modify_zip_file_bad_file_path(self):
        with self.assertRaises(FileNotFoundError):
            modify_zip_file('bad/path', copy_handler, None)
