from browser_use.agent.service import Agent
from langchain_openai import ChatOpenAI
# use anthropic sonnet 3.7 instead of gpt-4o
from langchain_anthropic import ChatAnthropic
import asyncio
from dotenv import load_dotenv
load_dotenv()

async def main():
    agent = Agent(
        task="Compare the price of gpt-4o and DeepSeek-V3",
        llm=ChatAnthropic(model="claude-3-5-sonnet-20240620"),
    )
    await agent.run()

asyncio.run(main())
