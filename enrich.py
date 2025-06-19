import json, re, requests
from playwright.sync_api import sync_playwright
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/113.0.0.0 Safari/537.36"

def get_search_links(query, serper_api_key):
    """
    Search Google using Serper API and return a list of links.
    """
    try:
        res = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": serper_api_key, "Content-Type": "application/json"},
            json={"q": query, "gl": "us", "hl": "en", "num": 10},
        )
        return [r["link"] for r in res.json().get("organic", [])]
    except Exception as e:
        print(f"[ERROR] Serper search failed: {e}")
        return []

def scrape_pages(links):
    """
    Scrape visible text from up to 5 links using Playwright.
    """
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
            except Exception as e:
                print(f"[WARN] Failed to scrape {link}: {e}")
                continue
        try:
            page.close()
        except Exception:
            pass
        browser.close()
    return "\n\n---\n\n".join(results)

def extract_enriched_profile(name, title, web_content, api_key):
    """
    Use LLM to extract a structured profile from web content.
    """
    system_prompt = (
        "You are a research assistant for a business team. Given the name and title of a speaker and some web search results, "
        "extract a detailed professional profile. Return structured JSON with: "
        "name, title, summary, achievements, public_content, links, outreach_message. "
        "The outreach message should come from NxtWave, an ed-tech company training Indian students to be software engineers, "
        "highlighting collaboration opportunities."
    )
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7, google_api_key=api_key)
    web_content = web_content[:15000] if len(web_content) > 15000 else (web_content if len(web_content) > 100 else "No web content found.")
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
        print(f"[ERROR] LLM enrichment failed for {name}: {e}")
        return {"name": name, "title": title, "summary": "", "achievements": [], "public_content": [], "links": [], "outreach_message": ""}

def enrich_speakers(google_api_key, serper_api_key, input_file="speakers.json", output_file="speakers_info.json", progress_callback=None):
    """
    Enrich all speakers in input_file and save to output_file.
    Optionally call progress_callback(current, total) after each speaker.
    """
    with open(input_file, "r", encoding="utf-8") as f:
        speakers = json.load(f)
    enriched = []
    total = len(speakers)
    for idx, spk in enumerate(speakers, 1):
        name, title = spk.get("name"), spk.get("title")
        links = get_search_links(f"{name} {title} site:linkedin.com OR site:github.com", serper_api_key)
        if not links:
            links = get_search_links(f"{name} {title}", serper_api_key)
        content = scrape_pages(links)
        enriched.append(extract_enriched_profile(name, title, content, google_api_key))
        print(f"[INFO] Enriched {idx}/{total} speakers.")
        if progress_callback:
            progress_callback(idx, total)
    print(f"[INFO] Enriched {len(enriched)} speakers.")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)