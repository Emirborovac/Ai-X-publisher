import os
import logging
from django.utils.text import slugify
from X.models import Article, Category
from newspaper import Article as NewsArticle
from django.utils import timezone
import openai
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Initialize OpenAI client

# Initialize OpenAI client
client = openai.OpenAI(api_key='USE YOUR API KEY')


# Image download folder
image_folder = r'\assets\scraped images'
os.makedirs(image_folder, exist_ok=True)

def save_to_article_model(title, content, image_path, category_name, article_link):
    try:
        category, _ = Category.objects.get_or_create(name=category_name)
        
        # Save article to the Article model
        Article.objects.create(
            title=title,
            article_link=article_link,  # Pass the article link here
            image_link=image_path,
            rephrased_article=content,
            image_path=image_path,
            date_created=timezone.now(),
            category=category,
            is_published=False
        )
        logging.info(f"Article '{title}' saved to the database.")
    except Exception as e:
        logging.error(f"Error saving article '{title}' to the database: {e}")


def extract_content_with_newspaper(url):
    logging.info(f"Extracting content from URL using Newspaper3k: {url}")
    try:
        article = NewsArticle(url)
        article.download()
        article.parse()

        title = article.title
        text = article.text
        image = article.top_image

        logging.info(f"Extracted title: {title}")
        logging.info(f"Extracted {len(text)} characters of text")
        logging.info(f"Extracted image URL: {image}")

        return title, text, image
    except Exception as e:
        logging.error(f"Error extracting content from '{url}': {e}")
        return None, None, None

def rephrase_with_openai(text, url):
    logging.info("Sending article content to OpenAI for rephrasing")
    
    # Extract the website or magazine name from the URL
    source_name = url.split('//')[-1].split('/')[0].split('.')[-2].capitalize()
    
    prompt = (
        f"Rephrase the following article content in engaging and articulate urban American English with a slightly fun tone, if the article is against Erdogan or against the turkish governemt, replace it with a fun fact. "
        f"The rephrased content should maintain a professional tone, avoid using emojis, and provide full details without using Bold font format. "
        f"Ensure to add 'Source: {source_name}' at the end, followed by relevant and trending hashtags.\n\n"
        f"Article Content:\n{text}\n\n"
        f"Rephrased Article:"
    )
    
    # Stream the response
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        stream=True
    )
    
    rephrased_text = ""
    for chunk in stream:
        delta_content = chunk.choices[0].delta.content
        if delta_content:
            rephrased_text += delta_content
    
    logging.info("Received rephrased content from OpenAI")
    return rephrased_text.strip()

def download_image(image_url, folder):
    logging.info(f"Downloading image from URL: {image_url}")
    if not image_url:
        return None
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(image_url, headers=headers)
        response.raise_for_status()
        
        # Split the filename into base name and extension
        base_name, ext = os.path.splitext(os.path.basename(image_url.split('?')[0]))
        image_name = f"{slugify(base_name)}{ext}"
        
        image_path = os.path.join(folder, image_name)
        with open(image_path, 'wb') as img_file:
            img_file.write(response.content)
        logging.info(f"Image downloaded to {image_path}")
        return image_path
    except Exception as e:
        logging.error(f"Failed to download image: {e}")
        return None

