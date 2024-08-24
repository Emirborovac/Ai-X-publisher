from django.test import TestCase
from scraper.rephrase_utils import save_to_article_model

class ImportTest(TestCase):
    def test_import(self):
        self.assertIsNotNone(save_to_article_model)
