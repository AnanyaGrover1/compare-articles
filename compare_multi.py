import os
import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
import openai
from dotenv import load_dotenv
import requests
import nltk
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag

import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


load_dotenv()


# Download required NLTK resources if not already downloaded
# nltk.download('maxent_ne_chunker')
# nltk.download('words')
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('stopwords')


# Get API key.
api_key = os.getenv("OPEN_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_KEY")
PERIGON_KEY = os.getenv("PERIGON_KEY")

st.title("Compare News Articles")

# Accept user input for a single URL.
url = st.text_input("Enter the article's URL: ")


def get_article_headline(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)

    if not response.ok:
        st.error(f"Error fetching article: Status code {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    headline = soup.find('h1')

    # If the headline isn't found in <h1>, try the Open Graph title.
    if not headline:
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title.get('content')

    return headline.get_text().strip() if headline else None


# Function to extract keywords based on importance from a news headline
# def extract_keywords(headline):
#     # Tokenize the headline
#     tokens = word_tokenize(headline)

#     # Remove stop words
#     stop_words = set(stopwords.words('english'))
#     filtered_tokens = [
#         token for token in tokens if token.lower() not in stop_words]

#     # Part-of-speech tagging
#     tagged = pos_tag(filtered_tokens)

#     # Identify important words - proper nouns (NNP), singular nouns (NN), and plural nouns (NNS)
#     keywords = [word for word,
#                 tag in tagged if tag in ('NNP', 'NN', 'NNS')]

#     return keywords

# Function that uses OpenAI's completion endpoint to extract keywords from a headline
def extract_keywords(headline):
    try:
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=f"Please list the most relevant keywords from the following news headline, "
            f"including any proper nouns, unique phrases, and important concepts. "
            f"These keywords should enable someone to understand the main focus of the article without reading it. "
            f"Present the keywords as a comma-separated list.\n\n"
            f"Headline: \"{headline}\"",
            max_tokens=60,
            temperature=0,  # deterministic output
            api_key=api_key
        )
        keywords = response.choices[0].text.strip()
        # Assuming the model responds with comma-separated keywords
        return keywords.split(', ')
    except openai.error.OpenAIError as e:
        print(f"OpenAI error: {e}")
        return []


def fetch_article_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        article = soup.find('article')
        text = article.get_text(separator='\n', strip=True)

        return text
    except Exception as e:
        st.warning(f"Could not fetch article from {url}. Error: {e}")
        return None

# Function to find related articles using NewsAPI and keywords extracted


def find_related_articles(keywords):
    query = ' '.join(keywords)  # Combine keywords into a single query string
    query = urllib.parse.quote_plus(query)  # URL-encode the query string
    print(query)
    related_urls = []

    try:
        # Make a request to the News API to get related articles.
        # news_api_url = f'https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}'
        news_api_url = f'https://api.goperigon.com/v1/all?q={query}&apiKey={PERIGON_KEY}&sourceGroup=top100'
        response = requests.get(news_api_url)
        data = response.json()

        if 'articles' in data:
            # Limit to first 5 related articles
            for article in data['articles'][:5]:
                if article['url'] != "https://removed.com":
                    related_urls.append(article['url'])

            if not related_urls:
                st.warning(
                    "No related articles found. Try a different headline or adjust your keywords.")
        else:
            st.warning("Error fetching related news articles from News API: " +
                       data.get('message', 'Unknown error.'))

    except Exception as e:
        st.error(f"Error fetching related articles: {e}")

    return related_urls


def fetch_article_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        article = soup.find('article')
        text = article.get_text(separator='\n', strip=True)

        return text
    except Exception as e:
        st.warning(
            f"Unfortunately, this article could not be scraped from {url}.")
        return None


# Button to find related articles
if st.button("Find Related Articles"):
    if url:
        # Extract the article headline from the user-provided URL.
        headline = get_article_headline(url)

        if headline:
            st.write(f"Headline Found: {headline}")

            # Extract keywords from the headline
            keywords = extract_keywords(headline)
            st.write(f"Keywords Extracted: {keywords}")

            related_urls = find_related_articles(keywords)
            article_content = []
            first_article = fetch_article_content(url)
            if first_article:
                article_content.append(first_article)

            if related_urls:
                st.write("Related articles found:")
                for related_url in related_urls:
                    st.write(related_url)
                    article = fetch_article_content(related_url)
                    if article:
                        article_content.append(article)
                        if len(article_content) >= 3:
                            break
                    else:
                        continue

                message = f"""Frames are the way media outlets select, organize, and present information to the audience.
            1. Read these three articles about the same news event (the content is provided below) and understand their perspectives.
            2. Begin by identifying points where all articles agree on the news event's details.
            3. Then, pinpoint any factual discrepancies between the articles.
            4. Finally, analyze the differences in how the articles frame the event and their viewpoints, including any selective omissions of information.

            Now, Summarize the articles together in three sets of bullet points:

            * Points of agreement between the three articles
            * Points of factual disagreement, if any
            * Differences in framing and viewpoint, and selective omissions:"""

                for i, content in enumerate(article_content):
                    message += f"Article {i+1}:\n{content}\n\n"

                message += """

            Comparison:"""

                print(message)

                response = openai.ChatCompletion.create(
                    model="gpt-4-1106-preview",
                    messages=[{"role": "user", "content": message}],
                    max_tokens=1000,
                    api_key=api_key,
                )

                # Display the summarized content.
                summarized_content = response.choices[0].message['content'].strip(
                )
                st.subheader(
                    "Comparative summary of top three articles found:")

                st.write(summarized_content)
            else:
                st.warning(
                    "No related articles found. Please try a different headline.")
        else:
            st.warning(
                "Could not extract the headline from the article. Please check if the URL is correct or try another URL.")
    else:
        st.warning("Please enter a URL to find related articles.")
