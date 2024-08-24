import os
import requests
import logging
import json
from urllib.parse import urljoin
from django.utils import timezone
from bs4 import BeautifulSoup
from lxml import etree, html
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import openai
from scraper.models import ScrapedArticle, ScrapedCategory
from django.db import IntegrityError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize OpenAI API
openai.api_key = 'ADD YOUR API KEY'
client = openai.OpenAI(api_key=openai.api_key)

news_categories = [
    "Politics", "Business and Finance", "Technology", "Health and Science",
    "Entertainment", "Sports", "Lifestyle", "World News", "Education",
    "Opinion", "Science and Environment", "Culture and Society"
]

def fetch_html(url):
    logging.info(f"Fetching HTML content from URL: {url}")

    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        logging.info(f"Fetched {len(response.text)} characters of HTML content")
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error encountered when fetching {url}: {e}")
        return None

def fetch_html_with_selenium(url):
    logging.info(f"Attempting to fetch HTML content from URL using Selenium: {url}")

    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920x1080")

    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//body"))
        )
        selenium_html = driver.page_source
        logging.info(f"Selenium fetched {len(selenium_html)} characters of HTML content")
        return selenium_html
    except Exception as e:
        logging.error(f"Error initializing Selenium WebDriver: {e}")
        return None
    finally:
        driver.quit()

def extract_outer_html(html_content, selector):
    logging.info(f"Extracting outer HTML with selector: {selector}")
    if selector.startswith('/') or selector.startswith('('):
        tree = html.fromstring(html_content)
        elements = tree.xpath(selector)
        outer_html = ' '.join([etree.tostring(element, pretty_print=True, encoding='unicode') for element in elements])
        logging.info(f"Extracted {len(elements)} elements with the XPath selector: {selector}")
    else:
        soup = BeautifulSoup(html_content, 'html.parser')
        elements = soup.select(selector)
        outer_html = ' '.join([str(element) for element in elements])
        logging.info(f"Extracted {len(elements)} elements with the CSS selector: {selector}")
    return outer_html

def send_to_gpt4(content, base_url):
    logging.info("Sending content to GPT-4 for processing")
    
    max_content_length = 15000
    all_results = []

    while content:
        part = content[:max_content_length]
        content = content[max_content_length:]

        prompt = f"""
        You are a JSON generator.

        Please organize the available blog posts links, with their titles, their publishing dates, and their categories.
        Return the data strictly in the following JSON format:

        [
            {{
                "Title": "string",
                "Link": "string",
                "Date": "string",
                "Category": "string"
            }},
            ...
        ]

        Only include a link in the "Link" field if it is explicitly found in the content; do not construct links from titles or any other text.
        Ensure the links are complete by prepending the base URL if necessary.
        Leave the "Date" field empty if not found.

        - The final output must be valid JSON only, with no additional text, explanations, or notes.
        - If no data is found in the content, return an empty JSON array: [].
        - Ensure that each element in the JSON array is properly formatted and that the JSON is closed correctly.

        The possible categories are: {', '.join(news_categories)}

        Base URL: {base_url}

        Content:
        {part}
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a JSON generator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,
                temperature=0.2
            )

            result = response.choices[0].message.content.strip()

            # Attempt to parse JSON immediately to catch errors
            json_result = json.loads(result)
            all_results.extend(json_result)

        except json.JSONDecodeError:
            logging.warning("Received content that does not appear to be valid JSON. Skipping this part.")
            continue
        except Exception as e:
            logging.error(f"Error processing GPT-4 response: {e}")
            continue

        logging.info(f"Received response from GPT-4: {result[:200]}...")
    
    combined_results = json.dumps(all_results, ensure_ascii=False)
    return combined_results

def process_extracted_data(data, base_url):
    logging.info(f"Raw GPT-4 output for debugging: {data}")
    try:
        blog_posts = json.loads(data)
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON: {e}")
        return []

    for post in blog_posts:
        post['Link'] = urljoin(base_url, post['Link'])
    
    logging.info(f"Processed {len(blog_posts)} blog posts")
    return blog_posts

from django.utils.dateparse import parse_datetime
from django.db import IntegrityError
import logging

def save_scraped_articles_to_db(posts):
    saved_count = 0
    for post in posts:
        category_name = post.get('Category', 'Uncategorized')
        category, _ = ScrapedCategory.objects.get_or_create(name=category_name)
        
        try:
            # Parse the date if available; otherwise, use the default
            date_str = post.get('Date', None)
            if date_str:
                date_published = parse_datetime(date_str)
                if not date_published:
                    logging.warning(f"Failed to parse date '{date_str}' for article '{post['Title']}'")
                    date_published = timezone.now()
            else:
                date_published = timezone.now()

            # Use get_or_create to avoid duplicates
            article, created = ScrapedArticle.objects.get_or_create(
                article_link=post['Link'],
                defaults={
                    'title': post['Title'],
                    'category': category,
                    'date_published': date_published,
                    'content': post.get('Content', '')
                }
            )
            if created:
                saved_count += 1
                logging.info(f"Created new article in the database: {post['Title']}")
            else:
                logging.info(f"Article already exists in the database: {post['Title']}")
        
        except IntegrityError as e:
            logging.error(f"Integrity error when trying to save article '{post['Title']}' with link '{post['Link']}': {e}")
        except Exception as e:
            logging.error(f"Unexpected error when saving article '{post['Title']}' with link '{post['Link']}': {e}")

    logging.info(f"Processed and saved {saved_count} posts to the database")
    return saved_count

def process_website(url, selectors, limit=None):
    logging.info(f"Processing website: {url}")

    html_content = fetch_html(url)
    if not html_content or not html_content.strip():
        logging.warning(f"No content or inaccessible website for {url}. Trying Selenium...")
        html_content = fetch_html_with_selenium(url)
    
    if not html_content or not html_content.strip():
        logging.error(f"Failed to fetch content from {url} even with Selenium. Skipping website.")
        return 0
    
    saved_articles_count = 0

    for selector in selectors:
        if limit and saved_articles_count >= limit:
            break
        
        selector = selector.strip()
        if not selector:
            logging.warning(f"Empty selector found for {url}. Skipping.")
            continue
        
        content = extract_outer_html(html_content, selector)
        if not content.strip():
            logging.warning(f"No content extracted with selector: {selector} on URL: {url}.")
            continue

        gpt_response = send_to_gpt4(content, url)
        fetched_posts = process_extracted_data(gpt_response, url)

        # Save the articles to the database
        saved_count = save_scraped_articles_to_db(fetched_posts)

        saved_articles_count += saved_count
        if limit and saved_articles_count >= limit:
            break

    return saved_articles_count

