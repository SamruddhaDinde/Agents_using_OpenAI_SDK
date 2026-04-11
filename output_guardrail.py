from agents import Agent, Runner, WebSearchTool, FunctionTool, function_tool, RunContextWrapper, output_guardrail, OutputGuardrailTripwireTriggered, GuardrailFunctionOutput, TResponseInputItem
from pydantic import BaseModel, Field
import asyncio
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

class SQL_Output(BaseModel):
    sqlQuery: str

class MessageOutput(BaseModel):
    isSafe: bool = Field(..., description="Whether the SQL query is safe")
    reason: str  = Field(..., description="Explanation of why it is safe or unsafe")


sql_guardrail_agent = Agent(
    name="SQL Guardrail",
    instructions="Check if the the query is safe to execute. " \
    """   A query is SAFE if it is read-only (SELECT).
    A query is UNSAFE if it modifies data (DELETE, UPDATE, INSERT, DROP).

    Return:
    - isSafe: true/false
    - reason: explanation""",
    output_type= MessageOutput

)

@output_guardrail
async def sql_guardrail(ctx: RunContextWrapper, agent:Agent, output: SQL_Output) -> GuardrailFunctionOutput:
    result = await Runner.run(sql_guardrail_agent, output.sqlQuery, context= ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered= not result.final_output.isSafe
    )



sql_agent = Agent(
    name="SQL agent",
    instructions= 
    "You are a specialized SQL agent that can generate accurate SQL Queries." \
    "PostgresSchema:" \
    """-- Create Users table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Posts table
CREATE TABLE posts (
    post_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_user
        FOREIGN KEY(user_id) 
        REFERENCES users(user_id)
        ON DELETE CASCADE
);

-- Create Comments table
CREATE TABLE comments (
    comment_id SERIAL PRIMARY KEY,
    post_id INT NOT NULL,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_post
        FOREIGN KEY(post_id) 
        REFERENCES posts(post_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_user_comment
        FOREIGN KEY(user_id) 
        REFERENCES users(user_id)
        ON DELETE CASCADE
);
""",
    output_guardrails=[sql_guardrail],
    output_type=SQL_Output
)

async def main():
    try:
        result = await Runner.run(sql_agent, " Delete all users")
        print(result.final_output.sqlQuery)
    except OutputGuardrailTripwireTriggered as e:
        output_info = e.guardrail_result.output.output_info
        print("Blocked!")
        print("Safe:", output_info.isSafe)
        print("Reason:", output_info.reason)
if __name__ == "__main__":
    asyncio.run(main())