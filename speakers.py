import os
import re
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage
from playwright.sync_api import sync_playwright

load_dotenv()
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.5)
CHROME_PROFILE_PATH = os.getenv("CHROME_PROFILE_PATH")


def get_rendered_page_text(url):
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=CHROME_PROFILE_PATH,
            headless=False,
            args=["--start-maximized"],
        )
        page = browser.new_page()
        try:
            print(f"Visiting: {url}")
            page.goto(url, timeout=90000)
            input("⏸️ Press ENTER once the page is fully visible...")
            page.wait_for_load_state("networkidle")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(7000)
            return page.inner_text("body")
        except Exception as e:
            print(f"Error loading page: {e}")
            return ""
        finally:
            browser.close()


def extract_speakers_from_text(text: str):
    if len(text) > 12000:
        text = text[:12000]

    messages = [
        SystemMessage(content="Extract a list of speakers from this content. Give name and title in JSON array."),
        HumanMessage(content=text)
    ]
    try:
        response = llm.invoke(messages)
        content = re.sub(r"^```json|```$", "", response.content.strip(), flags=re.MULTILINE).strip("`\n ")
        match = re.search(r"\[\s*{.*?}\s*\]", content, re.DOTALL)
        return json.loads(match.group(0)) if match else []
    except Exception as e:
        print(f"Speaker extraction error: {e}")
        return []


def get_speakers_from_url(url):
    text = get_rendered_page_text(url)
    return extract_speakers_from_text(text) if len(text) > 300 else []
