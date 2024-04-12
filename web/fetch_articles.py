# filename: fetch_articles.py
import requests
from bs4 import BeautifulSoup

# URLs of the articles to fetch
urls = [
    "https://www.washingtonpost.com/politics/2022/06/24/supreme-court-ruling-abortion-dobbs/",
    "https://www.foxnews.com/politics/supreme-court-overturns-roe-v-wade-dobbs-v-jackson-womens-health-organization",
    "https://www.cnn.com/2022/06/24/politics/dobbs-mississippi-supreme-court-abortion-roe-wade/index.html"
]

def fetch_article_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
        soup = BeautifulSoup(response.content, 'html.parser')
        # Assuming the main content is within article tags
        article = soup.find('article')
        if article:
            return article.get_text()
        else:
            return "Article content not found."
    except requests.RequestException as e:
        return str(e)

# Fetch and print the content of each article
for url in urls:
    print(f"Content from {url}:\n")
    content = fetch_article_content(url)
    print(content)
    print("\n" + "-"*80 + "\n")