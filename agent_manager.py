from agents import Agent, Runner, WebSearchTool, FunctionTool, function_tool, RunContextWrapper
from pydantic import BaseModel
import asyncio


@function_tool
def get_plans():
     return [
            {"plan_id": '1', "price": 50, "speed": '30mb/s'},
            {"plan_id": '2', "price": 40, "speed": '30mb/s'},
        ]

planning_agent = Agent(
    name = "Planning agent",
    instructions = "You are an expert planning agent. Fetch the available plans from the internet",
   tools=[get_plans]
)

planning_tool = planning_agent.as_tool(
    tool_name="planning_tool",
    tool_description = "Fetches available plans"
)


agent = Agent(
    name = "sales agent",
    instructions= "You are an expert sales agent for an internet broadband company.Talk to the user and help them with what they need",
    tools = [planning_tool],
)


async def main():
    result = await Runner.run(agent, "Hello?")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())