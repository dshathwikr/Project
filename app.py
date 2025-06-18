import streamlit as st
import json
import asyncio
from speakers import get_speakers_from_url
from enrich import enrich_speakers
from browser_agent import get_browser_agent

import sys
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

st.set_page_config(page_title="Tech Speaker Extractor", layout="centered")
st.title("🎤 Tech Speaker Extractor & Enricher")

st.subheader("🔗 Option 1: Extract Speakers from a URL")
url = st.text_input("Enter the speaker page URL")

st.subheader("📂 Option 2: Upload Enriched JSON")
uploaded_file = st.file_uploader("Upload `speakers_info.json`", type="json")

# ✅ Always initialize this to avoid NameError
enriched = []

if st.button("Extract & Enrich"):
    if not url:
        st.warning("Please enter a valid URL.")
    else:
        with st.spinner("Extracting speakers from the webpage..."):
            speakers = get_speakers_from_url(url)

        if not speakers:
            st.error("No speakers found or extraction failed.")
        else:
            with open("speakers.json", "w", encoding="utf-8") as f:
                json.dump(speakers, f, indent=2, ensure_ascii=False)

            st.success(f"Extracted {len(speakers)} speakers. Enriching now...")

            with st.spinner("Enriching speaker profiles..."):
                enrich_speakers()

            st.success("Enrichment complete!")

            with open("speakers_info.json", "r", encoding="utf-8") as f:
                enriched = json.load(f)

elif uploaded_file:
    enriched = json.load(uploaded_file)
    st.success("Enriched data loaded successfully.")

# ✅ UI Display of Enriched Speakers
if enriched:
    st.subheader("✅ Enriched Speaker Profiles")
    updated_speakers = []

    for i, speaker in enumerate(enriched):
        with st.expander(f"{speaker.get('name', f'Speaker {i+1}')} — {speaker.get('title', '')}", expanded=False):
            st.markdown(f"**📝 Summary:** {speaker.get('summary', '')}")

            # Achievements
            achievements = speaker.get("achievements", [])
            if achievements:
                st.markdown("**🏆 Achievements:**")
                for item in achievements:
                    st.markdown(f"- {item}")
            else:
                st.info("No achievements listed.")

            # Public Content
            public_content = speaker.get("public_content", [])
            if public_content:
                st.markdown("**📣 Public Content:**")
                for item in public_content:
                    st.markdown(f"- {item}")
            else:
                st.info("No public content available.")

            # Links
            links = speaker.get("links", [])
            if links:
                st.markdown("**🔗 Links:**")
                for link in links:
                    st.markdown(f"[{link}]({link})", unsafe_allow_html=True)
            else:
                st.info("No links provided.")

            # Outreach Message Editor
            message = st.text_area(
                "✉️ Outreach Message",
                value=speaker.get("outreach_message", ""),
                key=f"msg_{i}",
                height=170
            )
            speaker["outreach_message"] = message

            # Approve Button
            if st.button("Approve and Send on LinkedIn", key=f"approve_{i}"):
                with st.spinner(f"Sending LinkedIn message to {speaker['name']}..."):
                    try:
                        get_browser_agent(speaker['name'], speaker['outreach_message'])
                        st.success(f"LinkedIn outreach task executed for {speaker['name']}")
                    except Exception as e:
                        st.error(f"Browser agent failed: {e}")

            updated_speakers.append(speaker)

    # Save + Download buttons
    if st.button("📅 Save Updated Results"):
        with open("speakers_info_updated.json", "w", encoding="utf-8") as f:
            json.dump(updated_speakers, f, indent=2, ensure_ascii=False)
        st.success("Updated outreach messages saved to `speakers_info_updated.json`.")

    st.download_button(
        label="⬇️ Download Updated JSON",
        data=json.dumps(updated_speakers, indent=2),
        file_name="speakers_info_updated.json",
        mime="application/json"
    )
