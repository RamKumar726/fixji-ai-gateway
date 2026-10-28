from langchain.agents import create_agent
from langchain_openai import AzureChatOpenAI
from fastmcp.client import Client
from langchain.agents.middleware import HumanInTheLoopMiddleware 
from langgraph.checkpoint.memory import InMemorySaver
from .config import settings
from .mcp_tools import load_tools
from .prompts import SYSTEM_PROMPT



def build_llm() -> AzureChatOpenAI:
    return AzureChatOpenAI(model= settings.AZURE_OPENAI_DEPLOYMENT)


async def build_agent(token: str):
    client = Client(settings.MCP_URL, auth = token)
    tools = await load_tools(client)
    checkpointer = InMemorySaver()
    return create_agent(
        model=build_llm(),
        tools=tools, 
        system_prompt=SYSTEM_PROMPT,
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on = {"create_booking" : True},
            )
        ],
        checkpointer = checkpointer,
    )
