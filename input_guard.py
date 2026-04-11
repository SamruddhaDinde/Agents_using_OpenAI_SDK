from agents import Agent, Runner, WebSearchTool, FunctionTool, function_tool, RunContextWrapper, input_guardrail, InputGuardrailTripwireTriggered, GuardrailFunctionOutput, TResponseInputItem
from pydantic import BaseModel
import asyncio
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

class isMath(BaseModel):
    is_math_query: bool
    reasoning: str

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking only math queries",
    output_type=isMath
)
@input_guardrail
async def math_guardrail(ctx: RunContextWrapper[None], agent: Agent, input : str |list[TResponseInputItem]) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered= not result.final_output.is_math_query
    )
math_agent = Agent(
    name = " Maths Agent",
    instructions="You are an expert at solving math questions.",
    input_guardrails=[math_guardrail]

)

async def main():
    try:
        result = await Runner.run(math_agent, "write a code to add 7 numbers")
        print(result.final_output)
    except InputGuardrailTripwireTriggered:
        print("Not a math query")
if __name__ == "__main__":
    asyncio.run(main())