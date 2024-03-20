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

from googlesearch import search
search("Google")

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
            engine="gpt-3.5-turbo-instruct",  # or another powerful engine like "gpt-4"
            prompt=f"Please list the most relevant keywords from the following news headline, "\
            f"including any proper nouns, unique phrases, and important concepts. "\
            f"These keywords should enable someone to understand the main focus of the article without reading it. "\
            f"Present the keywords as a comma-separated list.\n\n"\
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


# Function to find related articles using NewsAPI and keywords extracted
def find_related_articles(keywords):
    query = ' '.join(keywords)  # Combine keywords into a single query string
    query = urllib.parse.quote_plus(query)  # URL-encode the query string
    print(query)
    related_urls = []

    try:
        # Make a request to the GNews API to get related articles.
        news_api_url = f'https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}'
        response = requests.get(news_api_url)
        data = response.json()

        if 'articles' in data:
            # Limit to first 5 related articles
            for article in data['articles'][:10]:
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

            if related_urls:
                st.write("Related articles found:")
                for related_url in related_urls:
                    st.write(related_url)

                # Use OpenAI's GPT to summarize the articles.
                # Prepare the message for the ChatGPT API.
                message = f"Read and summarize these articles: {', '.join(related_urls)}"
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "user", "content": message}
                    ],

                    max_tokens=1000,
                    api_key=api_key,
                )

                # Display the summarized content.
                summarized_content = response.choices[0].message['content'].strip(
                )
                st.subheader("Summary:")
                st.write(summarized_content)
            else:
                st.warning(
                    "No related articles found. Please try a different headline.")
        else:
            st.warning(
                "Could not extract the headline from the article. Please check if the URL is correct or try another URL.")
    else:
        st.warning("Please enter a URL to find related articles.")
