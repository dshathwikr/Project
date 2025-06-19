# Tech Speaker Extractor and Enricher

This app extracts speaker information from event/conference web pages, enriches their profiles using web search and LLMs, and helps automate LinkedIn outreach.

## Features

- Extract speakers (name, title) from a given URL using browser automation and LLMs.
- Enrich speaker profiles with web search, summaries, achievements, and outreach messages.
- Approve and automate LinkedIn outreach via a browser agent.
- Streamlit UI for easy interaction.

---

## Setup Instructions

### 1. Clone or Download the Repository

```bash
git clone https://github.com/dshathwikr/Project.git
cd Project
```

### 2. Install Python (3.9+ recommended)

Ensure Python is installed and available in your PATH.

### 3. Create and Activate a Virtual Environment (optional but recommended)

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 4. Install Dependencies

Install all required packages using `requirements.txt`:

```bash
pip install -r requirements.txt
```

**Install Playwright browsers:**

```bash
playwright install
```

### 5. Configure API Keys using `.env`

Create a `.env` file in the project directory with the following content:

```
GOOGLE_API_KEY=your_google_api_key_here
SERPER_API_KEY=your_serper_api_key_here
```

- **Google API Key**: For Gemini LLM (https://makersuite.google.com/app/apikey)
- **Serper API Key**: For Google Search (https://serper.dev)

The app will automatically load these keys.

### 6. Chrome Profile Path

- For browser automation, specify a Chrome user profile directory (e.g., `C:\Users\<user>\AppData\Local\Google\Chrome\User Data\Profile 1`).
- You can use the default or create a new one for this app.

---

## Running the App

```bash
streamlit run app.py
```

- Open the provided local URL in your browser.
- Enter your Chrome profile path in the sidebar.
- Enter a speaker page URL or upload a JSON file to start.

---

## Notes

- The app uses Playwright for browser automation. The first run may take longer as browsers are installed.
- For LinkedIn outreach, you may need to log in manually when prompted.
- All data is saved locally as `speakers.json`, `speakers_info.json`, and `speakers_info_updated.json`.

---

## Troubleshooting

- **Playwright errors**: Ensure browsers are installed (`playwright install`).
- **API errors**: Double-check your API keys and quotas in `.env`.
- **Chrome profile issues**: Make sure the path is correct and not in use by another Chrome instance.

---

## License

MIT License

---

## Credits

- [LangChain](https://github.com/langchain-ai/langchain)
- [Google Gemini](https://ai.google.dev/)
- [Serper.dev](https://serper.dev/)
- [Playwright](https://playwright.dev/)
- [Serper.dev](https://serper.dev/)
- [Playwright](https://playwright.dev/)
