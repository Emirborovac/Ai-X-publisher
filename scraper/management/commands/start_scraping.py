import logging
from django.core.management.base import BaseCommand
from scraper.models import ScrapedArticle, ScrapedCategory
from X.models import WebsiteInput
from scraper.utils import process_website

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Command(BaseCommand):
    help = 'Start scraping articles from the websites defined in WebsiteInput model'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, help='Limit the number of articles to scrape', default=20)

    def handle(self, *args, **kwargs):
        limit = kwargs['limit']
        articles_scraped = 0

        websites = WebsiteInput.objects.all()

        for website in websites:
            if articles_scraped >= limit:
                break
            articles_scraped += self.scrape_website(website, limit - articles_scraped)

        self.stdout.write(self.style.SUCCESS(f'Scraping completed successfully. Total articles scraped: {articles_scraped}'))

    def scrape_website(self, website, remaining_limit):
        logging.info(f"Fetching content from {website.url}")

        selectors = website.selectors.split(';')
        selectors = [selector.strip() for selector in selectors if selector.strip()]

        initial_count = ScrapedArticle.objects.count()
        
        process_website(website.url, selectors)
        
        final_count = ScrapedArticle.objects.count()
        new_articles = final_count - initial_count
        
        # Ensure we do not exceed the limit
        if new_articles > remaining_limit:
            # Delete the excess articles
            excess_articles = new_articles - remaining_limit
            # Get the IDs of the articles to delete
            latest_articles_ids = ScrapedArticle.objects.order_by('-date_published').values_list('id', flat=True)[:excess_articles]
            # Delete the articles by their IDs
            ScrapedArticle.objects.filter(id__in=latest_articles_ids).delete()
            new_articles = remaining_limit

        return new_articles
