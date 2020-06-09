from django.test import TestCase, RequestFactory
from template_engines.tests.fake_app.models import Bidon
from template_engines.tests.fake_app.views import WeasyprintTemplateView


class OdtTemplateTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.object = Bidon.objects.create(name='Michel')
        self.request = self.factory.get('')

    def test_view_works(self):
        WeasyprintTemplateView.template_name = 'pdf/template.pdf'
        response = WeasyprintTemplateView.as_view()(self.request, **{'pk': self.object.pk}).render()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content)

        self.assertEqual(response.content[:4], b'%PDF')
