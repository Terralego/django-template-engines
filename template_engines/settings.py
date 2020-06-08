from django.conf import settings

ODT_ENGINE_SUB_DIRNAME = getattr(settings, 'ODT_ENGINE_SUB_DIRNAME', 'odt')
ODT_ENGINE_APP_DIRNAME = getattr(settings, 'ODT_ENGINE_APP_DIRNAME', 'templates')

DOCX_ENGINE_SUB_DIRNAME = getattr(settings, 'DOCX_ENGINE_SUB_DIRNAME', 'docx')
DOCX_ENGINE_APP_DIRNAME = getattr(settings, 'DOCX_ENGINE_APP_DIRNAME', 'templates')

WEASYPRINT_ENGINE_SUB_DIRNAME = getattr(settings, 'DOCX_ENGINE_SUB_DIRNAME', 'pdf')
WEASYPRINT_ENGINE_APP_DIRNAME = getattr(settings, 'DOCX_ENGINE_APP_DIRNAME', 'templates')
