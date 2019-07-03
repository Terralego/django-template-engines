from tempfile import NamedTemporaryFile

from django.conf import settings
from django.template.response import TemplateResponse

from requests import post


class ToPdfResponse(TemplateResponse):

    @property
    def rendered_content(self):
        content = super().rendered_content
        temp_file = NamedTemporaryFile()
        with open(temp_file.name, 'wb') as writer:
            writer.write(content)
        pdf_convertor_host = getattr(settings, 'PDF_CONVERTOR_HOST', 'localhost')
        pdf_convertor_port = getattr(settings, 'PDF_CONVERTOR_PORT', 9999)
        url = f'http://{pdf_convertor_host}:{pdf_convertor_port}/'
        files = {'file': ('tempalte.odt', open(temp_file.name, 'rb'), 'application/vnd.oasis.opendocument.text')}
        response = post(url, files=files)
        return response.content
