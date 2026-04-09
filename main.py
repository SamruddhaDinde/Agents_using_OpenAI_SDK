from dotenv import load_dotenv
load_dotenv()
import asyncio
from agents import Agent, Runner

location = 'India'

def getInstructions(context, agent):
    if location == 'India':
        return "Start with Namaste and greet with the name of the user"
    else:
        return "Say hello and greet with the name of the user"


agent = Agent(
    name="Hello Agent",
    instructions= getInstructions,
      
    
 
)

async def main():
    result = await Runner.run(agent, "Hello my name is Sam")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())