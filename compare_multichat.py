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

# create an AssistantAgent instance named "academic"
academic = autogen.AssistantAgent(
    name="academic",
    llm_config=llm_config,
    system_message="""You are an academic scholar in Media Studies. You specialize in analyzing news articles,
    identifying points of view, and differentiating between factual information and narrative framing. """,
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
            * Differences in framing, where frames are abstractions or angles that guide how information is constructed and communicated to the audience.
            * Differences in viewpoints, where viewpoints are defined as value-based opinions and attitudes.
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

# create an AssistantAgent instance named "engineer"
# engineer = autogen.AssistantAgent(
#     name="engineer",
#     llm_config=llm_config,
#     system_message="""Engineer. You write python/shell code to solve tasks including finding information online through Google Search API. Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the user_proxy.
# Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the user_proxy.
# If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
# """,
#     code_execution_config={"work_dir": "web", "use_docker": False},
#     # Limit the number of consecutive auto-replies.

#     description="""This agent will write python/shell code to solve tasks when asked by another agent to do so.
#     """


# )


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

# planner = autogen.AssistantAgent(
#     name="Planner",
#     system_message="""Planner. Suggest a plan. Revise the plan based on feedback from admin, until admin approval.
# The plan may involve an engineer who can write code and a media expert, an analyst, and a factchecker who don't write code.
# Explain the plan first. Be clear which step is performed by an engineer, and which step is performed by a media expert, the analyst, and the factchecker.
# """,
#     llm_config=llm_config,
# )

groupchat = autogen.GroupChat(
    agents=[user_proxy, academic, factchecker,
            legal, summarizer], messages=[], max_round=10
)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)


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
