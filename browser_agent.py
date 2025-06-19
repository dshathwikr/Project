import asyncio
from browser_use import Agent, Browser, BrowserConfig
from langchain_google_genai import ChatGoogleGenerativeAI

def get_browser_agent(person_name: str, outreach_message: str, chrome_profile_path: str):
    """
    Automate LinkedIn outreach using browser agent.
    """
    task = f"""
    1. Open LinkedIn and search for {person_name}.
    2. Open their profile.
    3. If Connect is available, click it, then Add a Note, then paste:
       \"{outreach_message}\"
    4. If Message is available instead, open and send the same message.
    5. If neither is available, skip.
    """

    agent = Agent(
        task=task,
        browser=Browser(config=BrowserConfig(user_data_dir=chrome_profile_path)),
        llm=ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.4),
    )

    try:
        asyncio.run(agent.run())
    except Exception as e:
        print(f"[ERROR] Browser agent failed: {e}")