from django.core.management.base import BaseCommand
from scraper.utils import process_website

class Command(BaseCommand):
    help = 'Scrapes articles from a given URL and saves them into the database.'

    def add_arguments(self, parser):
        parser.add_argument('url', type=str, help='The URL of the website to scrape.')

    def handle(self, *args, **kwargs):
        url = kwargs['url']
        process_website(url)
        self.stdout.write(self.style.SUCCESS('Successfully scraped articles from "%s"' % url))
