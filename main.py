from browser_use.agent.service import Agent
from langchain_openai import ChatOpenAI
# use anthropic sonnet 3.7 instead of gpt-4o
from langchain_anthropic import ChatAnthropic
import asyncio
from dotenv import load_dotenv
load_dotenv()

async def main():
    #agent1 = Agent(
    #    task="Go on walmart website and search for 乌龟, the chinese name for turtle, and see if the website supports this search, report the result.",
    #    llm=ChatAnthropic(model="claude-3-7-sonnet-20250219"),
    #    task_name="walmart"
    #)
    agent2 = Agent(
        task="Go on taobao.com website and search for 牛奶, the chinese name for milk, and see if the website supports this search, report the result.",
        llm=ChatAnthropic(model="claude-3-7-sonnet-20250219"),
        task_name="taobao"
    )
    
    
    #await agent1.run()
    await agent2.run()

asyncio.run(main())
