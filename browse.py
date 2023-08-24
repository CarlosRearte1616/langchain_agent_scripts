from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent

from langchain.agents.agent_toolkits import PlayWrightBrowserToolkit
from langchain.tools.playwright.utils import (
    create_async_playwright_browser,
    create_sync_playwright_browser,
)

# from langchain.chat_models import ChatAnthropic

sync_browser = create_sync_playwright_browser()
browser_toolkit = PlayWrightBrowserToolkit.from_browser(sync_browser=sync_browser)
tools = browser_toolkit.get_tools()
print(tools)

# llm = ChatAnthropic(temperature=0)

llm = ChatOpenAI(
    temperature=0,
    openai_api_key="",
    model="gpt-3.5-turbo",
)  # Also works well with Anthropic models
agent_chain = initialize_agent(
    tools,
    llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

response = agent_chain.run(
    input="Navigate to langchain.com and get the header's content."
)
print(response)
