import os
import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
from openai import OpenAI
from dotenv import load_dotenv
import requests
import newspaper

import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


load_dotenv()


# Get API key.
api_key = os.getenv("OPENAI_API_KEY")
# NEWS_API_KEY = os.getenv("NEWS_KEY")
PERIGON_KEY = os.getenv("PERIGON_KEY")

st.title("Welcome to PRISM 👋")

st.sidebar.success("Switch to another interface")

st.subheader(
    "Enter the URL of any news article. PRISM will compare and summarize it with alternate news coverage on the topic.")


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


# Function that uses OpenAI's completion endpoint to extract keywords from a headline
def extract_keywords(headline):
    try:

        client = OpenAI()

        user_message = f"""Please list the most relevant keywords from the following news headline including any proper
        nouns, unique phrases, and important concepts. These keywords should enable someone to understand the main focus
        of the article without reading it. Present the keywords as a comma-separated list.\n\n"
        Headline: \"{headline}\""""

        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "user", "content": user_message}
            ],
            max_tokens=60,
            temperature=0
            # api_key=api_key
        )

        keywords = response.choices[0].message.content.strip()
        # Assuming the model responds with comma-separated keywords
        return keywords.split(', ')

    except Exception as e:
        st.warning(f"An unexpected error occurred: {e}")
        raise


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

    # Attempt with BeautifulSoup
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        content = soup.find('article')

        if content is None:
            for tag in ['main', 'div']:
                content = soup.find(tag)
                if content:
                    break

        if content is not None:
            text = content.get_text(separator='\n', strip=True)
            return text
    except requests.exceptions.RequestException as e:
        # print statements for error
        print(
            f"BeautifulSoup method failed for {url}. Error: {e}. Attempting newspaper3k...")

    # If BeautifulSoup method didn't work, fallback to newspaper3k
    try:
        article = newspaper.Article(url=url, language='en')
        article.download()
        article.parse()
        return str(article.text)
    except Exception as e:
        # If newspaper3k also fails, then print an error message
        print(
            f"Could not fetch article content from {url} using both BeautifulSoup and newspaper3k. Error: {e}.")
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

                message = f"""Frames are the way media outlets select, organize, and present information to the audience. For example, The UK
        media initially framed the migrant crisis in terms of negative economic impact, using dehumanizing language
        like "swarms of migrants" and "cockroaches." However, after the widely shared image of three-year-old Syrian
        Aylan Kurdi, the narrative shifted towards humanizing migrants, altering public perception.

        Viewpoints are defined as value-based opinions and attitudes. The viewpoint could be of the author of the
        news story or it could be presented through the inclusion of quotes and opinions that reflect the subjective
        values of individuals or groups. For instance, coverage of an environmental policy reducing carbon emissions
        may highlight perspectives of activists and experts supporting it, emphasizing the value of protecting the
        planet, while other stories may focus on opposing viewpoints of industry leaders, such as concerns about jobs
        being lost.

        Given the above information, perform the following task step by step:
            1. Read these articles about the same news event (the content is provided below) and understand them.
            2. Begin by identifying points where both articles agree on the news event's factual details.
            3. Then, pinpoint any factual discrepancies between the articles.
            4. Next, analyze the differences in frames between the articles.
            5. Now, analyze the differences in the viewpoints presented in each article.
            6. Finally, notice any selective omissions of information.

            Now, summarize the articles together in five sets of bullet points:

            * Upto five main points of agreement between the articles
            * Any points of factual disagreement
            * Differences in framing
            * Differences in viewpoints
            * Selective omissions

            Here are the articles:"""

                for i, content in enumerate(article_content):
                    message += f"Article {i+1}:\n{content}\n\n"

                message += """

                Comparison:"""

                client = OpenAI()

                response = client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "user", "content": message}
                    ],
                    max_tokens=1000,
                    # api_key=api_key
                )

                # Extract the "content" part under "choices" in the response
                comparison_paragraph = response.choices[0].message.content.strip(
                )

                # Display the comparison
                st.subheader(
                    "Comparative summary of top three articles found:")
                st.write(comparison_paragraph)

            else:
                st.warning(
                    "No related articles found. Please try a different headline.")
        else:
            st.warning(
                "Could not extract the headline from the article. Please check if the URL is correct or try another URL.")
    else:
        st.warning("Please enter a URL to find related articles.")
