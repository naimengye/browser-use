from browser_use.agent.service import Agent
from langchain_openai import ChatOpenAI
# use anthropic sonnet 3.7 instead of gpt-4o
from langchain_anthropic import ChatAnthropic
import asyncio
from dotenv import load_dotenv
load_dotenv()

async def main():
    #input the task from a file of multiple tasks, with each task a name and a task description
    with open("tasks.txt", "r") as f:
        for line in f:
            name, task = line.strip().split(":",1)
            agent = Agent(
                task=task,
                llm=ChatAnthropic(model="claude-3-7-sonnet-20250219"),
                task_name=name
            )
            await agent.run()   

asyncio.run(main())
