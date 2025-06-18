import time
import asyncio
import subprocess
import os
from dotenv import load_dotenv
import browser_use
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
browser_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
CHROME_PROFILE_PATH = os.getenv("CHROME_PROFILE_PATH")

def launch_debugging_browser():
    subprocess.run(["taskkill", "/f", "/im", "chrome.exe"], capture_output=True, check=False)
    time.sleep(2)
    return subprocess.Popen(
        [
            browser_path,
            "--remote-debugging-port=9222",
            f"--user-data-dir={CHROME_PROFILE_PATH}",
            "--no-first-run",
            "--disable-default-apps",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

# def get_browser_agent(task: str):

#     async def main():
#         browser = browser_use.Browser(
#             config=browser_use.BrowserConfig(chrome_instance_path=browser_path)
#         )
#         agent = browser_use.Agent(
#             task=task,
#             llm=ChatGoogleGenerativeAI(model="gemini-2.0-flash"),
#             browser=browser,
#         )
#         return await agent.run()

#     return asyncio.run(main())

def get_browser_agent(person_name: str, outreach_message: str):
    from browser_use import Agent
    from langchain_google_genai import ChatGoogleGenerativeAI
    import asyncio

    task = f"""
    You are an assistant using a browser to complete a LinkedIn task.
    1. Open https://www.linkedin.com and log in.
    2. Search for the person: "{person_name}".
    3. Click on their profile from the search results.
    4. If a "Connect" button is available:
       - Click "Connect".
       - Then click "Add a note".
       - Paste the following message:
         "{outreach_message}"
       - Click "Send".
    5. If already connected and a "Message" button is available:
       - Click it and send the same message.
    6. If neither is available, skip the person.
    """

    agent = Agent(
        task=task,
        llm=ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.4)
    )

    asyncio.run(agent.run())
