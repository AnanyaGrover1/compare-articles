# filename: scrape_articles.py
import requests
from bs4 import BeautifulSoup

# URLs of the articles to scrape
urls = [
    "https://www.washingtonpost.com/politics/2022/06/24/supreme-court-ruling-abortion-dobbs/",
    "https://www.foxnews.com/politics/supreme-court-overturns-roe-v-wade-dobbs-v-jackson-womens-health-organization",
    "https://www.cnn.com/2022/06/24/politics/dobbs-mississippi-supreme-court-abortion-roe-wade/index.html"
]

def scrape_content(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the content using BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            # Extract the main content of the article
            # This might need to be adjusted depending on the structure of the webpage
            article_body = soup.find('article')
            if article_body:
                # Extract text from the article body
                paragraphs = article_body.find_all('p')
                article_text = ' '.join(p.get_text() for p in paragraphs)
                return article_text
            else:
                print(f"Article body not found for URL: {url}")
        else:
            print(f"Failed to retrieve content from URL: {url}, Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while scraping URL: {url}, Error: {e}")

# Scrape content from each URL and print it
for url in urls:
    content = scrape_content(url)
    if content:
        print(f"Content from {url}:\n{content}\n")