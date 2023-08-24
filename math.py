from pydantic import BaseModel, Field
from langchain import LLMMathChain, SerpAPIWrapper
from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.tools import BaseTool, StructuredTool, Tool, tool


class CalculatorInput(BaseModel):
    question: str = Field()


tools = []

llm = ChatOpenAI(
    temperature=0,
    openai_api_key="",
    model="gpt-3.5-turbo",
)

llm_math_chain = LLMMathChain(llm=llm, verbose=True)

tools.append(
    Tool.from_function(
        func=llm_math_chain.run,
        name="Calculator",
        description="useful for when you need to answer questions about math",
        args_schema=CalculatorInput
        # coroutine= ... <- you can specify an async method if desired as well
    )
)

# Construct the agent. We will use the default agent type here.
# See documentation for a full list of options.
agent = initialize_agent(
    tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
)

agent.run("what is the value of variable x in expression 4*x^2=4?")
