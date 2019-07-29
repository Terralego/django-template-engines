from io import BytesIO
from zipfile import ZipFile

from django.test import TestCase

from template_engines.backends.utils import modify_libreoffice_doc
from test_template_engines.tests.backends.backend_settings import ODT_TEMPLATE_PATH, DOCX_TEMPLATE_PATH


class TestUtils(TestCase):

    def test_modify_libreoffice_doc_with_odt_works(self):
        new_file = modify_libreoffice_doc(ODT_TEMPLATE_PATH, 'content.xml', '')
        # Checks the return type
        self.assertIsInstance(new_file, bytes)

        buffer = BytesIO(new_file)
        with ZipFile(buffer, 'r') as buffer_zip_obj:
            with ZipFile(ODT_TEMPLATE_PATH, 'r') as odt_zip_obj:
                buffer_filename_list = list(map(lambda e: e.filename, buffer_zip_obj.infolist()))
                odt_filename_list = list(map(lambda e: e.filename, odt_zip_obj.infolist()))
                # Checks that the archive contains the same files
                self.assertEqual(buffer_filename_list, odt_filename_list)

                for filename in odt_filename_list:
                    if filename != 'content.xml':
                        # Checks that the files are dientical
                        self.assertEqual(buffer_zip_obj.read(filename), odt_zip_obj.read(filename))
                    else:
                        self.assertEqual(buffer_zip_obj.read(filename), b'')

    def test_modify_libreoffice_doc_with_docx_works(self):
        new_file = modify_libreoffice_doc(DOCX_TEMPLATE_PATH, 'word/document.xml', '')
        # Checks the return type
        self.assertIsInstance(new_file, bytes)

        buffer = BytesIO(new_file)
        with ZipFile(buffer, 'r') as buffer_zip_obj:
            with ZipFile(DOCX_TEMPLATE_PATH, 'r') as odt_zip_obj:
                buffer_filename_list = list(map(lambda e: e.filename, buffer_zip_obj.infolist()))
                odt_filename_list = list(map(lambda e: e.filename, odt_zip_obj.infolist()))
                # Checks that the archive contains the same files
                self.assertEqual(buffer_filename_list, odt_filename_list)

                for filename in odt_filename_list:
                    if filename != 'word/document.xml':
                        # Checks that the files are dientical
                        self.assertEqual(buffer_zip_obj.read(filename), odt_zip_obj.read(filename))
                    else:
                        self.assertEqual(buffer_zip_obj.read(filename), b'')
