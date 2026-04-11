from agents import Agent, Runner, WebSearchTool, FunctionTool, function_tool, RunContextWrapper
from pydantic import BaseModel
import asyncio
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

@function_tool
def get_plans():
     return [
            {"plan_id": '1', "price": 50, "speed": '30mb/s'},
            {"plan_id": '2', "price": 70, "speed": '100mb/s'},
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

refund_agent = Agent(
    name = "Refund agent",
    instructions = "You are an expert refund agent, and authorized with issuing refunds",
    tools=[process_refunds]

)
planning_agent = Agent(
    name = "Planning agent",
    instructions = "You are an expert planning agent. Fetch the available plans from the internet",
   tools=[get_plans]
)

planning_tool = planning_agent.as_tool(
    tool_name="planning_tool",
    tool_description = "Fetches available plans"
)
sales_agent = Agent(
    name = "sales agent",
    instructions= "You are an expert sales agent for an internet broadband company.Talk to the user and help them with what they need",
    tools = [planning_tool],
)


reception_agent = Agent(
    name = "Reception Agent",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX}" \
    "You are the customer facing agent expert in" \
    "understanding what the customer needs and then route them " \
    "or handoff them to the right agent",
    handoff_description="You have two agents at your disposal:" \
    "sales agent: expert in handling user queries like plans and pricing" \
    "refund agent: expert in handling refund requests and approving them",
    handoffs=[sales_agent, refund_agent]
)

async def main():
    result = await Runner.run(reception_agent, "Hey there, I am cust567,  I need a refund becuase the service is slow!!!")
    print(result.final_output)
    print(result.raw_responses)
if __name__ == "__main__":
    asyncio.run(main())