from dotenv import load_dotenv
load_dotenv()
import asyncio
import os
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import httpx
from pydantic import BaseModel
import smtplib
from typing_extensions import TypedDict
from agents import Agent, Runner, WebSearchTool, FunctionTool, function_tool, RunContextWrapper

class WeatherData(BaseModel):
    degree: int
    condition: str

@function_tool
async def get_weather(city: str)->str:
    """Fetch the current weather for the given city.
    Args:
        city: The city to fetch weather for
    """
    url = f'https://wttr.in/{city.lower()}?format=%C+%t'
    headers = {"User-Agent":"curl/7.68.0"}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

        return f'The weather of {city} is {response.text.strip()}'
    except Exception as e:
        return f'Could not fetch weather for {city}: {str(e)}'

@function_tool
async def send_email(address: str, subject: str, body: str):
    """
    Send the weather data to the address.

    Args:
        address: The email address the data needs to sent to.
        subject: The subject of the email.
        body: The body of the email.
    """
    port = 465
    smtp_server = "smtp.gmail.com"
    sender_email = os.getenv("APP_NAME")
    password = os.getenv("PASSWORD")

    # Build properly formatted email
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = address
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))


    try: 
        with smtplib.SMTP_SSL(smtp_server, port) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, address, message.as_string())
        print("email sent successfully")
    except Exception as e:
        print(f"Errors: {e}")

agent = Agent(   
    name="Weather Agent",
    tools=[
        get_weather, WebSearchTool(),
],
    output_type= WeatherData,
)


async def main():
    result = await Runner.run(agent, "What is the weather in Sydney ?")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())