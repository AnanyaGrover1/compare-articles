import os
import requests
from bs4 import BeautifulSoup
import streamlit as st
import openai

from dotenv import load_dotenv

load_dotenv()


api_key = os.getenv("OPEN_API_KEY")

st.title("Compare news articles")

# Accept user input for the URLs
url1 = st.text_input("Enter the first article's URL: ")
url2 = st.text_input("Enter the second article's URL: ")


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


if st.button("Compare Articles"):
    if url1 and url2:
        # Fetch articles' contents
        article1_content = fetch_article_content(url1)
        article2_content = fetch_article_content(url2)

        if article1_content and article2_content:
            # Create the user message for ChatGPT, with the actual content instead of URLs
            user_message = f"""Read these two articles about the same news event (the content is provided below). Summarize the articles together in three sets of bullet points:
            * Points of agreement between first article and second article
            * Points of factual disagreement, if any
            * Differences in framing and viewpoint, and selective omissions:

            Article 1 Content:
            {article1_content}

            Article 2 Content:
            {article2_content}

            Comparison: """

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1000,  # Increased max_tokens in case articles are long
                api_key=api_key
            )

            # Extract the "content" part under "choices" in the response
            comparison_paragraph = response.choices[0].message['content'].strip(
            )

            # Display the comparison
            st.subheader("Comparison:")
            st.write(comparison_paragraph)
        else:
            st.warning("Could not fetch content from one or both URLs.")
    else:
        st.warning("Please enter both URLs to compare.")
