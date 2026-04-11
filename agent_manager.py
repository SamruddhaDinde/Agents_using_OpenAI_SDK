from agents import Agent, Runner, WebSearchTool, FunctionTool, function_tool, RunContextWrapper
from pydantic import BaseModel
import asyncio


@function_tool
def get_plans():
     return [
            {"plan_id": '1', "price": 50, "speed": '30mb/s'},
            {"plan_id": '2', "price": 40, "speed": '30mb/s'},
        ]
@function_tool
async def process_refunds(cust_id: str, reason: str) -> str:
    """
    Process refunds based on genuine reasons.
    Args:
        cust_id: the customer id of the customer.
        reason: the reason why the cutomer wants a refund.
    """
    message = f"The refund is processed for {cust_id} for {reason}"
    with open("refunds.txt", "a") as f:
        f.write(message +"\n")
    return message

planning_agent = Agent(
    name = "Planning agent",
    instructions = "You are an expert planning agent. Fetch the available plans from the internet",
   tools=[get_plans]
)

planning_tool = planning_agent.as_tool(
    tool_name="planning_tool",
    tool_description = "Fetches available plans"
)



refund_agent = Agent(
    name = "Refund agent",
    instructions = "You are an expert refund agent, and authorized with issuing refunds",
    tools=[process_refunds]

)
refund_tool = refund_agent.as_tool(
    tool_name="refund_tool",
    tool_description = "Issues Refunds"
)



agent = Agent(
    name = "sales agent",
    instructions= "You are an expert sales agent for an internet broadband company.Talk to the user and help them with what they need",
    tools = [planning_tool, refund_tool],
)


async def main():
    result = await Runner.run(agent, "Hey I had plan, I need a refund right now because I am moving places, my id is cust124?")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())