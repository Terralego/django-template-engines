from bs4 import BeautifulSoup
from io import BytesIO
from zipfile import ZipFile

from django.test import TestCase

from template_engines.backends.utils import clean_tags, modify_content_document
from template_engines.backends.utils_docx import add_image_in_docx_template
from ..settings import (ODT_TEMPLATE_PATH, DOCX_TEMPLATE_PATH, IMAGE_PATH, BAD_TAGS_XML,
                        CLEAN_CONTENT)


class TestUtils(TestCase):

    def test_modify_content_document_with_odt_works(self):
        new_file = modify_content_document(ODT_TEMPLATE_PATH, ['content.xml'],
                                           BeautifulSoup('<content-merged></content-merged>', 'lxml'))
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
                        self.assertEqual(buffer_zip_obj.read(filename), b'<?xml version="1.0" encoding="UTF-8"?>\n')

    def test_modify_content_document_with_docx_works(self):
        new_file = modify_content_document(DOCX_TEMPLATE_PATH, ['word/document.xml'],
                                           BeautifulSoup('<word-document-merged></word-document-merged>', 'lxml'))
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
                        self.assertEqual(buffer_zip_obj.read(filename), b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')

    def test_add_image_in_docx_template_works(self):
        img_content = open(IMAGE_PATH, 'rb').read()
        new_file = add_image_in_docx_template(
            open(DOCX_TEMPLATE_PATH, 'rb').read(),
            {
                'name': 'makinacorpus.png',
                'content': img_content,
            })
        self.assertIsInstance(new_file, bytes)
        buffer = BytesIO(new_file)
        with ZipFile(buffer, 'r') as buffer_zip_obj:
            img = buffer_zip_obj.read('word/media/makinacorpus.png')
            self.assertEqual(img_content, img)
            self.assertEqual(
                buffer_zip_obj.read('word/_rels/document.xml.rels'),
                b''.join([
                    b'<?xml version="1.0" encoding="UTF-8"?>',
                    b'\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
                    b'<Relationship Id="rId1" ',
                    b'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" ',
                    b'Target="styles.xml"/><Relationship Id="rId2" ',
                    b'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/fontTable"',
                    b' Target="fontTable.xml"/><Relationship Id="rId3" ',
                    b'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings"',
                    b' Target="settings.xml"/>\n<Relationship Id="makinacorpus.png" ',
                    b'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"',
                    b' Target="media/makinacorpus.png"/></Relationships>'
                ])
            )

    def test_remove_bad_tags(self):
        with open(BAD_TAGS_XML) as reader:
            content = reader.read()
        clean_content = clean_tags(content)
        self.assertNotEqual(content, clean_content)
        with open(CLEAN_CONTENT) as reader:
            self.assertEqual(reader.read(), clean_content)
