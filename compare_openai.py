import os
import streamlit as st
import newspaper
from openai import OpenAI
import requests
from bs4 import BeautifulSoup

from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(
    page_title="PRISM",
    page_icon="👋",
)
st.write("# Welcome to PRISM! Enter the URLs of upto three different news articles on the same topic, which you wish to compare.")

st.sidebar.success("Switch to another interface")


st.title("Compare news articles")

# Accept user input for the URLs
url1 = st.text_input("Enter the first article's URL: ")
url2 = st.text_input("Enter the second article's URL: ")
# New line for optional third URL input
url3 = st.text_input("Enter the third article's URL (optional): ")


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


def process_articles(urls, mode):
    # Fetch content for non-empty URLs
    article_contents = [fetch_article_content(url) for url in urls if url]

    if not all(article_contents):
        st.warning("Could not fetch content from one or more URLs.")
        return

    # Concatenate article contents for the user message
    articles_comparison_texts = "\n\n".join(
        [f"Article {i+1} Content:\n{content}" for i, content in enumerate(article_contents)])

    if mode == "Zero shot":
        user_message = f"""Summarize these articles about the same news event (the content is provided below) in five sets of bullet points:
        * Up to five main points of agreement between the articles
        * Any points of factual disagreement
        * Differences in framing
        * Differences in viewpoints
        * Selective omissions

        {articles_comparison_texts}

        Comparison:
        """
    elif mode == "Chain of Thought":
        user_message = f"""

        Frames are the way media outlets select, organize, and present information to the audience. For example, The UK
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

            Here are the articles:

        {articles_comparison_texts}

        Comparison:
        """

    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "user", "content": user_message}
        ],
        max_tokens=1000,  # Increased max_tokens in case articles are long
        # api_key=api_key
    )

    # Extract the "content" part under "choices" in the response
    comparison_paragraph = response.choices[0].message.content.strip()

    # Display the comparison
    st.subheader("Comparison:")
    st.write(comparison_paragraph)


urls = [url1, url2]  # Start with two URLs
if url3:  # Add the third URL if present
    urls.append(url3)

if st.button("Zero shot"):
    process_articles(urls, "Zero shot")
if st.button("Chain of Thought"):
    process_articles(urls, "Chain of Thought")
