# Tech Speaker Extractor & Enricher

This app extracts speaker information from event/conference web pages, enriches their profiles using web search and AI, and helps automate LinkedIn outreach.

## Features

- Extracts speaker names and titles from a given URL.
- Enriches speaker profiles with summaries, achievements, links, and outreach messages using AI and web search.
- Lets you review, edit, and send outreach messages via LinkedIn using a browser automation agent.
- Supports uploading and downloading enriched speaker JSON files.

## Setup

1. **Clone or Download the Repository**

2. **Create and Activate a Virtual Environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright Browsers**
   ```bash
   playwright install
   ```

5. **Set up your `.env` file**

   Copy `.env` and fill in:
   - `GOOGLE_API_KEY` (for Gemini/Google GenAI)
   - `SERPER_API_KEY` (get from [serper.dev](https://serper.dev/))
   - `USER_AGENT` (default is fine)
   - `CHROME_PROFILE_PATH` (path to your Chrome user profile for persistent login)

6. **(Optional) Log in to LinkedIn in your Chrome profile**
   - Open Chrome with the profile path in `CHROME_PROFILE_PATH` and log in to LinkedIn.

## Usage

1. **Start the Streamlit app**
   ```bash
   streamlit run app.py
   ```

2. **Extract & Enrich Speakers**
   - Enter a URL of a speakers page and click "Extract & Enrich".
   - Or upload an existing `speakers_info.json` file.

3. **Review and Outreach**
   - Review and edit the enriched speaker profiles and outreach messages.
   - Click "Approve and Send on LinkedIn" to automate outreach (requires LinkedIn login in your Chrome profile).

4. **Save or Download**
   - Save updated results or download the enriched JSON.

## Notes

- The app uses Google Gemini (via `langchain-google-genai`) and Serper.dev for AI and search.
- Browser automation for LinkedIn uses your local Chrome profile for authentication.
- For best results, ensure your Chrome profile is logged in to LinkedIn.

## Troubleshooting

- If browser automation fails, check your `CHROME_PROFILE_PATH` and ensure Chrome is not running in the background.
- If extraction/enrichment fails, check your API keys and internet connection.

## License

For internal/demo use only.
