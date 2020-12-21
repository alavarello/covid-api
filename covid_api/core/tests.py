from django.test import TestCase
from covid_api.core.services import CovidService, QueryWrapper
# Create your tests here.


class CovidServiceTestCase(TestCase):
    def setUp(self):
        """Not implemented"""

    def test_get_data_len(self):
        """FALTA"""
        data = CovidService.get_query()
        self.assertGreater(data.count(), 10)



