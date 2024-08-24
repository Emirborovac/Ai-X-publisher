from django.core.management.base import BaseCommand
from scraper.rephrase_utils import save_to_article_model, image_folder, extract_content_with_newspaper, rephrase_with_openai, download_image
from scraper.models import ScrapedArticle

class Command(BaseCommand):
    help = 'Rephrases scraped articles and saves them to the Article model'

    def handle(self, *args, **kwargs):
        # Fetch all unscraped articles
        scraped_articles = ScrapedArticle.objects.all()
        
        for scraped_article in scraped_articles:
            self.process_article(scraped_article)
    
    def process_article(self, scraped_article):
        try:
            # Extract content using Newspaper3k
            extracted_title, article_text, image_link = extract_content_with_newspaper(scraped_article.article_link)
            
            if article_text:
                # Rephrase content using OpenAI
                rephrased_text = rephrase_with_openai(article_text, scraped_article.article_link)
                
                # Download image
                local_image_path = download_image(image_link, image_folder)
                
                # Save the rephrased article to the Article model
                save_to_article_model(
                    title=extracted_title,
                    content=rephrased_text,
                    image_path=local_image_path,
                    category_name=scraped_article.category.name,
                    article_link=scraped_article.article_link  # Pass the article link here
                )
                
                self.stdout.write(self.style.SUCCESS(f'Successfully processed and saved article: {extracted_title}'))
            else:
                self.stdout.write(self.style.WARNING(f'No valid content found for {scraped_article.article_link}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error processing article '{scraped_article.article_link}': {e}"))
