import os
import autogen
import requests
from openai import OpenAI
from bs4 import BeautifulSoup
import newspaper
import json


from dotenv import load_dotenv

load_dotenv()


api_key = os.getenv("OPEN_API_KEY")

config_list = [
    {
        'model': 'gpt-4-1106-preview',
        'api_key': api_key

    }
]

llm_config = {
    "timeout": 600,
    "seed": 57,
    "config_list": config_list,
    "temperature": 0
}

# create an AssistantAgent instance named "academic"
academic = autogen.AssistantAgent(
    name="academic",
    llm_config=llm_config,
    system_message="""You are an academic scholar in Media Studies. You specialize in analyzing news articles,
    identifying points of view, and identifying frames in articles. Frames are abstractions or angles that guide how
    information is constructed and communicated to the audience. Viewpoints are defined as value-based opinions and
    attitudes, which could be of the author of the news story or be presented through quotes and opinions that reflect
    the subjective values of individuals or groups.""",
    code_execution_config={"work_dir": "web", "use_docker": False},


    description="""This agent goes first and analyzes the point of views and framing in the articles.
    """

)

# create an AssistantAgent instance named "summarizer"
summarizer = autogen.AssistantAgent(
    name="summarizer",
    llm_config=llm_config,
    system_message="""Comparative Summary Agent. Considering the views from the agents academic, factchecker, and legal, you synthesize
    all their respective insights and create a comparative summary of the news articles. You
    write the final summary in five sets of bullet points:
            * Upto five main points of agreement between the articles
            * Any points of factual disagreement
            * Differences in framing
            * Differences in viewpoints
            * Selective omissions
            """,
    code_execution_config={"work_dir": "web", "use_docker": False},
    # Limit the number of consecutive auto-replies.

    description="""This agent goes after all the other agents have offered their views and provides the final output to the user.
    """


)

# create an AssistantAgent instance named "factchecker"
factchecker = autogen.AssistantAgent(
    name="factchecker",
    llm_config=llm_config,
    system_message="""Fact checker. You can detect discrepancies and flag any potential inaccuracies
    or misleading claims in the articles.""",
    code_execution_config={"work_dir": "web", "use_docker": False},
    # Limit the number of consecutive auto-replies.


    description="""This agent is reponsible for flagging any misleading or unfounded claims.
    """


)

# create an AssistantAgent instance named "legal"
legal = autogen.AssistantAgent(
    name="legal",
    llm_config=llm_config,
    system_message="""Legal Analyst. You specialize in legal matters and Supreme Court jurisprudence.
    You can provide insights into Supreme Court rulings, legal principles, and their implications. """,
    code_execution_config={"work_dir": "web", "use_docker": False},
    # Limit the number of consecutive auto-replies.

    description="""This agent is reponsible for offering legal insights.
    """

)


# create a UserProxyAgent instance named "user_proxy"
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get(
        "content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir": "web",
        "use_docker": False,
    },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
    llm_config=llm_config,
    system_message="""You will execute any code that the engineer writes. Once the summarizer has given its summary, the task is complete. Reply TERMINATE if the task has been solved at full satisfaction.
Otherwise, reply CONTINUE, or the reason why the task is not solved yet.""",
)


groupchat = autogen.GroupChat(
    agents=[user_proxy, academic, factchecker,
            legal, summarizer], messages=[], max_round=10
)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)


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


# Get the news article links from the user
news_links = input(
    "Enter the URLs of the news articles you want to summarize, separated by commas: ").split(',')

# Fetch the article content first using the fetch_article_content function
article_contents = [fetch_article_content(url) for url in news_links]

# Create a formatted message with headings for each article and its content
message = ""
for i, content in enumerate(article_contents, start=1):
    message += f"Article {i}:\n{content}\n\n"

# the user enters the news article links and initiates the conversation with the assistant
user_proxy.initiate_chat(
    manager,
    speaker_selection_method="round_robin",

    message=f"""Read these different articles on the same news story, analyze, and summarize them:\n{message}""",

)
