import os
import autogen
import requests
from openai import OpenAI
from bs4 import BeautifulSoup


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

# create an AssistantAgent instance named "assistant"
assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config=llm_config,
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
    system_message="""Reply TERMINATE if the task has been solved at full satisfaction.
Otherwise, reply CONTINUE, or the reason why the task is not solved yet.""",
)

# Get the news article links from the user
# news_links = input(
#     "Enter the URLs of the news articles you want to summarize, separated by commas: ").split(',')

# Prepare the message with the news article links
# news_links_message = " ".join(news_links)

# the assistant receives a message from the user, which contains the task description
user_proxy.initiate_chat(
    assistant,
    message="""
Write the code for an autograder that evaluates a AI-generated summary against the ground truth summary. Ask the user to provide the ground truth as well as the AI output. Both summaries will consist of five sets of bullet points:

            * Upto five main points of agreement between the articles
            * Any points of factual disagreement
            * Differences in framing, where frames are the way media outlets select, organize, and present information to the audience.
            * Differences in viewpoints, where viewpoints are defined as value-based opinions and attitudes.
            * Selective omissions

""",
)
