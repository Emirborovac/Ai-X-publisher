from newspaper import Article

def fetch_news_article(url):
    # Initialize the Article object
    article = Article(url)

    # Download the article
    article.download()

    # Parse the article
    article.parse()

    # Print the title of the article
    print(f"Title: {article.title}\n")

    # Print the author(s) of the article
    print(f"Authors: {', '.join(article.authors)}\n")

    # Print the publication date (if available)
    print(f"Publication Date: {article.publish_date}\n")

    # Print the article text
    print("Article Text:")
    print(article.text)

    # Print the top image of the article
    print(f"\nTop Image: {article.top_image}\n")

    # Print the keywords of the article (if available)
    article.nlp()  # Perform natural language processing (NLP) to extract keywords
    print(f"Keywords: {', '.join(article.keywords)}\n")

# Example usage
url = "https://www.middleeasteye.net/news/barack-obama-makes-no-mention-gaza-war-dnc-speech"
fetch_news_article(url)
