import streamlit as st
import json
import asyncio
import os
from speakers import get_speakers_from_url
from enrich import enrich_speakers
from browser_agent import get_browser_agent

import sys
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

st.set_page_config(page_title="Tech Speaker Extractor", layout="centered")
st.title("Tech Speaker Extractor and Enricher")

st.sidebar.header("🔧 Configuration")
google_api_key = st.sidebar.text_input("Google API Key", value=os.environ.get('GOOGLE_API_KEY', ''))
serper_api_key = st.sidebar.text_input("Serper API Key", value=os.environ.get('SERPER_API_KEY', ''))
chrome_profile_path = st.sidebar.text_input("Chrome Profile Path", value="~/CustomChromeProfile")

# Save API keys to environment
if google_api_key:
    os.environ['GOOGLE_API_KEY'] = google_api_key
if serper_api_key:
    os.environ['SERPER_API_KEY'] = serper_api_key

# Validate API keys
if not google_api_key or len(google_api_key.strip()) < 10:
    st.sidebar.error("⚠️ Please enter a valid Google API key")
if not serper_api_key or len(serper_api_key.strip()) < 10:
    st.sidebar.error("⚠️ Please enter a valid Serper API key")

st.subheader("🌐 Option 1: Extract Speakers from a URL")
url = st.text_input("Enter the speaker page URL")

st.subheader("📁 Option 2: Upload Enriched JSON")
uploaded_file = st.file_uploader("Upload speakers_info.json", type="json")

enriched = []

extract_clicked = st.button("Extract and Enrich")

if extract_clicked:
    if not url:
        st.warning("Please enter a URL")
    elif not google_api_key or not serper_api_key:
        st.error("Please provide both API keys in the sidebar")
    else:
        with st.spinner("Extracting speakers from the webpage..."):
            try:
                speakers = get_speakers_from_url(url, google_api_key, chrome_profile_path)
            except Exception as e:
                st.error(f"Error occurred during extraction: {str(e)}")
                speakers = []
        if not speakers:
            st.error("No speakers found or extraction failed.")
        else:
            try:
                with open("speakers.json", "w", encoding="utf-8") as f:
                    json.dump(speakers, f, indent=2, ensure_ascii=False)
                st.success(f"✅ Extracted {len(speakers)} speakers. Enriching now...")

                progress_bar = st.progress(0)
                status_text = st.empty()
                enriched_count = [0]

                def progress_callback(current, total):
                    progress_bar.progress(current / total)
                    status_text.info(f"Enriched {current}/{total} speakers...")

                with st.spinner("Enriching speaker profiles..."):
                    enrich_speakers(
                        google_api_key,
                        serper_api_key,
                        progress_callback=progress_callback
                    )
                progress_bar.progress(1.0)
                status_text.success("🎉 Enrichment complete")

                try:
                    with open("speakers_info.json", "r", encoding="utf-8") as f:
                        enriched = json.load(f)
                    st.info(f"🔎 Enriched {len(enriched)} speakers.")
                    st.write(f"**Console:** Enriched {len(enriched)} speakers.")
                except Exception as e:
                    st.error(f"Failed to load enriched data: {e}")
            except Exception as e:
                st.error(f"Error during enrichment: {str(e)}")
elif uploaded_file:
    try:
        enriched = json.load(uploaded_file)
        if not isinstance(enriched, list) or not enriched:
            st.error("Uploaded file is empty or not a valid enriched speakers JSON.")
            enriched = []
        else:
            st.success("📄 Enriched data loaded successfully.")
            st.info(f"🔎 Enriched {len(enriched)} speakers.")
    except Exception as e:
        st.error(f"Failed to load uploaded file: {e}")
        enriched = []

if enriched:
    st.subheader("📌 Enriched Speaker Profiles")
    updated_speakers = []
    for i, speaker in enumerate(enriched):
        with st.expander(f"{speaker.get('name', f'Speaker {i+1}')} - {speaker.get('title', '')}"):
            st.markdown(f"**Summary:** {speaker.get('summary', '')}")
            for label, key in [("Achievements", "achievements"), ("Public Content", "public_content"), ("Links", "links")]:
                items = speaker.get(key, [])
                if items:
                    st.markdown(f"**{label}:**")
                    for item in items:
                        st.markdown(f"- {item}" if key != "links" else f"[{item}]({item})", unsafe_allow_html=True)
            message = st.text_area("✉️ Outreach Message", value=speaker.get("outreach_message", ""), key=f"msg_{i}", height=160)
            speaker["outreach_message"] = message
            if st.button("Approve and Open Browser Search", key=f"approve_{i}"):
                with st.spinner(f"Opening browser for {speaker.get('name', f'Speaker {i+1}')}..."):
                    try:
                        get_browser_agent(speaker.get('name', ''), message, chrome_profile_path)
                        st.success(f"✅ Browser search task launched for {speaker.get('name', f'Speaker {i+1}')}")
                    except Exception as e:
                        st.error(f"❌ Browser agent failed: {e}")
            updated_speakers.append(speaker)

    if st.button("📂 Save Updated Results"):
        try:
            with open("speakers_info_updated.json", "w", encoding="utf-8") as f:
                json.dump(updated_speakers, f, indent=2, ensure_ascii=False)
            st.success("✔️ Updated outreach messages saved.")
        except Exception as e:
            st.error(f"Failed to save updated results: {e}")

    st.download_button("⬇️ Download Updated JSON", data=json.dumps(updated_speakers, indent=2), file_name="speakers_info_updated.json", mime="application/json")
