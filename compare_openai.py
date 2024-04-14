import os
import requests
from bs4 import BeautifulSoup
import streamlit as st
from openai import OpenAI
import newspaper
import json

from dotenv import load_dotenv

load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")

st.title("Compare news articles")

# Accept user input for the URLs
url1 = st.text_input("Enter the first article's URL: ")
url2 = st.text_input("Enter the second article's URL: ")


# def fetch_article_content(url):
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

#     try:
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()

#         soup = BeautifulSoup(response.content, 'html.parser')

#         # Try to find the 'article' tag first
#         content = soup.find('article')

#         # If 'article' tag not found, try other methods
#         if content is None:
#             # Try finding the main body of text using common tags
#             for tag in ['main', 'div']:
#                 content = soup.find(tag)
#                 if content:
#                     break

#         # If still not found, return a descriptive error
#         if content is None:
#             raise ValueError(
#                 "Unable to locate the article's text. Please check the article structure.")

#         # Safely extract text now that we've ensured content is not None
#         text = content.get_text(separator='\n', strip=True)

#         return text
#     except Exception as e:
#         st.warning(f"Could not fetch article from {url}. Error: {e}")
#         return None


def fetch_article_content(url):
    try:
        # Initialize a newspaper article object
        article = newspaper.Article(url=url, language='en')

        # Download and parse the article
        article.download()
        article.parse()

        # Optionally to load additional NLP data
        # article.nlp()  # Uncomment to se nlp features like keywords or summary

        # returning only the article text
        return str(article.text)
    except Exception as e:
        st.warning(f"Could not fetch article from {url}. Error: {e}")
        return None


if st.button("Zero shot"):
    if url1 and url2:
        # Fetch articles' contents
        article1_content = fetch_article_content(url1)
        article2_content = fetch_article_content(url2)

        if article1_content and article2_content:
            # Create the user message for ChatGPT, with the actual content instead of URLs
            user_message = f"""Summarize these articles about the same news event (the content is provided below) in five sets of bullet points:
            * Upto five main points of agreement between the articles
            * Any points of factual disagreement
            * Differences in framing, where frames are the way media outlets select, organize, and present information to the audience.
            * Differences in viewpoints, where viewpoints are defined as value-based opinions and attitudes.
            * Selective omissions


            Article 1 Content:
            {article1_content}

            Article 2 Content:
            {article2_content}

            Comparison:
"""
            client = OpenAI()

            response = client.chat.completions.create(
                model="gpt-4",
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
        else:
            st.warning("Could not fetch content from one or both URLs.")
    else:
        st.warning("Please enter both URLs to compare.")


if st.button("Chain of Thought"):
    if url1 and url2:
        # Fetch articles' contents
        article1_content = fetch_article_content(url1)
        article2_content = fetch_article_content(url2)

        if article1_content and article2_content:
            # Create the user message for ChatGPT, with the actual content instead of URLs
            user_message = f"""Frames are the way media outlets select, organize, and present information to the audience.
            1. Read these two articles about the same news event (the content is provided below) and understand their perspectives.
            2. Begin by identifying points where both articles agree on the news event's details.
            3. Then, pinpoint any factual discrepancies between the articles.
            4. Finally, analyze the differences in how the articles frame the event and their viewpoints, including any selective omissions of information.

            Now, Summarize the articles together in five sets of bullet points:

            * Upto five main points of agreement between the articles
            * Any points of factual disagreement
            * Differences in framing, where frames are the way media outlets select, organize, and present information to the audience.
            * Differences in viewpoints, where viewpoints are defined as value-based opinions and attitudes.
            * Selective omissions

            Take note of the key points and frames presented in the first article.
            Article 1 Content:
            {article1_content}

            Take note of the key points and frames presented in the second article.

            Article 2 Content:
            {article2_content}

            After summarizing both articles individually, proceed to compare them directly.

            Comparison:"""

            client = OpenAI()

            response = client.chat.completions.create(
                model="gpt-4",
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
        else:
            st.warning("Could not fetch content from one or both URLs.")
    else:
        st.warning("Please enter both URLs to compare.")
