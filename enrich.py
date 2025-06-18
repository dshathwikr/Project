import json
import os
import re
import requests
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage
from playwright.sync_api import sync_playwright

load_dotenv()
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
USER_AGENT = os.getenv("USER_AGENT")


def get_search_links(query):
    try:
        response = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"},
            json={"q": query, "gl": "us", "hl": "en", "num": 10},
        )
        return [r["link"] for r in response.json().get("organic", [])]
    except Exception as e:
        print(f"Search error: {e}")
        return []


def scrape_pages(links):
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=USER_AGENT)
        page = context.new_page()
        for link in links[:5]:
            try:
                page.goto(link, timeout=15000)
                page.wait_for_load_state("domcontentloaded")
                text = page.inner_text("body")
                if len(text.strip()) > 100:
                    results.append(f"URL: {link}\n\n{text.strip()}")
            except:
                continue
        browser.close()
    return "\n\n---\n\n".join(results)


def extract_enriched_profile(name, title, web_content):
    system_prompt = (
        "You are a research assistant for a business team. Given the name and title of a speaker and some web search results, "
        "extract a detailed professional profile. Return structured JSON with: "
        "name, title, summary, achievements, public_content, links, outreach_message. "
        "The outreach message should come from NxtWave, an ed-tech company training Indian students to be software engineers, "
        "highlighting collaboration opportunities."
    )
    if len(web_content) < 100:
        web_content = "No web content found. Synthesize profile."
    if len(web_content) > 15000:
        web_content = web_content[:15000]
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Name: {name}\nTitle: {title}\n\n{web_content}"),
    ]
    try:
        res = llm.invoke(messages).content.strip()
        raw = re.sub(r"^```(?:json)?|```$", "", res, flags=re.MULTILINE).strip("`\n ")
        match = re.search(r"{.*}", raw, re.DOTALL)
        return json.loads(match.group(0))
    except Exception as e:
        return {
            "name": name,
            "title": title,
            "summary": "",
            "achievements": [],
            "public_content": [],
            "links": [],
            "outreach_message": "",
            "error": str(e),
        }


def enrich_speakers(input_file="speakers.json", output_file="speakers_info.json"):
    with open(input_file, "r", encoding="utf-8") as f:
        speakers = json.load(f)
    enriched = []
    for spk in speakers:
        name, title = spk.get("name"), spk.get("title")
        print(f"🔍 Researching: {name}")
        links = get_search_links(f"{name} {title} site:linkedin.com OR site:github.com")
        if not links:
            links = get_search_links(f"{name} {title}")
        content = scrape_pages(links)
        enriched.append(extract_enriched_profile(name, title, content))
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)
    print("✅ Saved to", output_file)
