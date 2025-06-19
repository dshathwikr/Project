import re, json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage
from playwright.sync_api import sync_playwright

def get_rendered_page_text(url, chrome_profile_path):
    """
    Render the page using Playwright and return the visible text.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=chrome_profile_path,
            headless=False,
            args=["--start-maximized"]
        )
        page = browser.new_page()
        try:
            page.goto(url, timeout=90000)
            input("🔓 Please log in if needed and press ENTER once the page is fully visible...")
            page.wait_for_load_state("networkidle")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(7000)
            text = page.inner_text("body")
            return text
        except Exception as e:
            print(f"[ERROR] Failed to render or extract text: {e}")
            return ""
        finally:
            try:
                page.close()
            except Exception:
                pass
            browser.close()

def extract_speakers_from_text(text: str, api_key: str):
    """
    Use LLM to extract speakers from text. Returns a list of dicts.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.5, google_api_key=api_key)
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
        print(f"[ERROR] LLM extraction failed: {e}")
        return []

def get_speakers_from_url(url, api_key: str, chrome_profile_path: str):
    """
    Main entry: get speakers from a URL using browser rendering and LLM extraction.
    """
    text = get_rendered_page_text(url, chrome_profile_path)
    if len(text) > 300:
        return extract_speakers_from_text(text, api_key)
    return []