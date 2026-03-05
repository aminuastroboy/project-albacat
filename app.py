import json
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Project ALBACAT",
    layout="wide"
)

# -------------------------
# Load catalog
# -------------------------
with open("catalog.json") as f:
    CATALOG = json.load(f)

# -------------------------
# Helpers
# -------------------------
def drive_preview(file_id):
    return f"https://drive.google.com/file/d/{file_id}/preview"

def drive_download(file_id):
    return f"https://drive.google.com/uc?export=download&id={file_id}"

def parse_date(d):
    try:
        return datetime.strptime(d, "%Y-%m-%d")
    except:
        return datetime.min

# -------------------------
# Header
# -------------------------
st.title("Project ALBACAT")
st.caption("History Audio Library • Albani Zaria")

# -------------------------
# Sidebar Filters
# -------------------------
with st.sidebar:

    st.header("Browse")

    search = st.text_input("Search")

    topics = sorted(set(x["topic"] for x in CATALOG))
    topic = st.selectbox("Topic", ["All"] + topics)

    series = sorted(set(x["series"] for x in CATALOG))
    series_select = st.selectbox("Series", ["All"] + series)

    sort = st.selectbox(
        "Sort",
        ["Newest", "Session Order", "A-Z"]
    )

# -------------------------
# Filtering
# -------------------------
items = []

for item in CATALOG:

    if topic != "All" and item["topic"] != topic:
        continue

    if series_select != "All" and item["series"] != series_select:
        continue

    if search and search.lower() not in str(item).lower():
        continue

    items.append(item)

# -------------------------
# Sorting
# -------------------------
if sort == "Newest":
    items.sort(key=lambda x: parse_date(x["date"]), reverse=True)

elif sort == "Session Order":
    items.sort(key=lambda x: x["sessionNumber"])

elif sort == "A-Z":
    items.sort(key=lambda x: x["title"])

# -------------------------
# Grid Display
# -------------------------
cols = st.columns(3)

for i, item in enumerate(items):

    col = cols[i % 3]

    with col:

        with st.container(border=True):

            st.subheader(item["title"])

            st.caption(
                f"{item['author']} • {item['series']}"
            )

            st.write(
                f"""
**Topic:** {item['topic']}  
**Session:** #{item['sessionNumber']}  
**Duration:** {item['duration']}  
**Language:** {item['language']}  
"""
            )

            st.write(item["description"])

            play = st.button(
                "▶ Play",
                key=item["id"]
            )

            st.link_button(
                "⬇ Download",
                drive_download(item["fileId"])
            )

            if play:

                st.session_state["player"] = item

# -------------------------
# Player
# -------------------------
st.divider()
st.header("Player")

if "player" not in st.session_state:

    st.info("Select a lecture to start playing")

else:

    item = st.session_state["player"]

    st.subheader(item["title"])

    st.components.v1.iframe(
        drive_preview(item["fileId"]),
        height=520
    )
