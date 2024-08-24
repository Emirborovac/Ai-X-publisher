import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from django.core.management.base import BaseCommand
from django.utils import timezone
from X.models import Article, PublishedArticle  # Replace 'X' with the actual name of your app

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s',
    handlers=[
        logging.FileHandler("post_articles.log"),
        logging.StreamHandler()
    ]
)

# Set up Chrome options
options = Options()
options.add_argument("--headless")  # Uncomment this to run headless if needed
options.add_argument("user-data-dir=C:/Users/YOUR USER/AppData/Local/Google/Chrome/User Data")#put your user here!
options.add_argument("profile-directory=Default")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--log-level=3")

# Set up the WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
# Parameters for tweet cycle
TWEETS_PER_CYCLE = 300  # Number of tweets per cycle
CYCLE_DURATION_SECONDS = 3600  # Duration of each cycle in seconds (1 hour)
COOLDOWN_SECONDS = 0  # No additional cooldown since the cycle should end and wait for the next hour

# Parameters for tweet cycle
#TWEETS_PER_CYCLE = 2  # Number of tweets per cycle (set to 300 for actual use)
#CYCLE_DURATION_SECONDS = 5  # Duration of each cycle in seconds (set to 3600 for 1 hour in actual use)
#COOLDOWN_SECONDS = 60  # Cooldown period after a cycle in seconds

def filter_non_bmp_chars(text):
    """Remove characters outside the Basic Multilingual Plane (BMP) to avoid issues with ChromeDriver."""
    return ''.join(c for c in text if ord(c) <= 0xFFFF)

def post_article(article, image_path=None):
    """Posts an article with text and an optional image."""
    try:
        article_text = filter_non_bmp_chars(article.rephrased_article)
        logging.info(f"Fetched article: {article.title}")
        logging.info(f"Article text: {article_text}")
        logging.info(f"Image path: {image_path if image_path else 'No image attached'}")

        logging.info("Waiting for the tweet input field to be visible...")
        wait = WebDriverWait(driver, 30)
        tweet_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[aria-label="Post text"]')))
        logging.info("Tweet input field identified.")

        logging.info("Entering tweet text...")
        tweet_input.click()
        tweet_input.send_keys(article_text)
        logging.info("Tweet text entered.")

        if image_path:
            logging.info("Uploading the image.")
            image_upload_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div[2]/div[1]/div/div/div/div[2]/div[2]/div[2]/div/div/nav/div/div[2]/div/div[1]/div/button')))
            
            # Scroll into view if necessary
            driver.execute_script("arguments[0].scrollIntoView(true);", image_upload_button)
            driver.execute_script("arguments[0].click();", image_upload_button)
            logging.info("Image upload button clicked via JavaScript.")

            image_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]')))
            image_input.send_keys(image_path)
            logging.info("Image path sent to input field.")

            time.sleep(5)  # Wait to ensure the image is uploaded

        logging.info("Waiting for the Post button to be clickable...")
        post_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div[2]/div[1]/div/div/div/div[2]/div[2]/div[2]/div/div/div/button')))
        
        # Scroll into view if necessary
        driver.execute_script("arguments[0].scrollIntoView(true);", post_button)
        driver.execute_script("arguments[0].click();", post_button)
        logging.info("Post button clicked via JavaScript. Tweet posted successfully.")

    except Exception as e:
        logging.error(f"Failed to post tweet: {e}")

def mark_as_published(article):
    """Marks the article as published and moves it to the PublishedArticle model."""
    try:
        article.is_published = True
        article.save()
        # Create a PublishedArticle object with correct fields
        PublishedArticle.objects.create(
            title=article.title,
            article_link=article.article_link,
            image_link=article.image_link,
            rephrased_article=article.rephrased_article,
            image_path=article.image_path,
            category=article.category,
            date_created=article.date_created,
            date_published=timezone.now()
        )
        logging.info(f"Article '{article.title}' marked as published and moved to PublishedArticle.")
    except Exception as e:
        logging.error(f"Failed to mark article '{article.title}' as published: {e}")

class Command(BaseCommand):
    help = 'Posts articles to X.com'

    def handle(self, *args, **kwargs):
        try:
            logging.info("Opening the X.com homepage...")
            driver.get("https://x.com/home")
            
            time.sleep(10)
            logging.info("Page loaded successfully.")

            articles_to_post = Article.objects.filter(is_published=False)
            logging.info(f"Found {articles_to_post.count()} articles to post.")

            tweet_count = 0
            cycle_start_time = time.time()

            for article in articles_to_post:
                if tweet_count == 0:
                    logging.info("Starting a new cycle of posting.")

                if tweet_count >= TWEETS_PER_CYCLE:
                    # Calculate elapsed time
                    elapsed_time = time.time() - cycle_start_time
                    logging.info(f"Cycle limit reached. Posted {tweet_count} tweets in {elapsed_time:.2f} seconds.")

                    # Wait for the cooldown period
                    time_to_wait = max(COOLDOWN_SECONDS - elapsed_time, 0)
                    logging.info(f"Cooldown period: Waiting for {time_to_wait} seconds before starting the next cycle.")
                    time.sleep(time_to_wait)

                    # Reset for the next cycle
                    tweet_count = 0
                    cycle_start_time = time.time()

                logging.info(f"Posting article: {article.title}")
                post_article(article, article.image_path)
                mark_as_published(article)
                tweet_count += 1

                time.sleep(3)  # Sleep between each tweet
                driver.refresh()  # Refresh the page after each article is posted

            logging.info("All articles have been posted successfully.")
        finally:
            logging.info("Closing the browser...")
            driver.quit()