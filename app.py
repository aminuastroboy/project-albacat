import json
import os
from datetime import datetime

import streamlit as st
from PIL import UnidentifiedImageError

CATALOG_PATH = "catalog.json"
TEAM_PATH = "team.json"


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def safe_logo(path, width):
    if not path:
        return
    try:
        st.image(path, width=width)
    except (UnidentifiedImageError, OSError):
        pass


def find_logo():
    for p in ["logo.png", "assets/logo.png", "assets/logo.jpg"]:
        if os.path.exists(p):
            return p
    return None


def parse_date(d):
    try:
        return datetime.strptime(d, "%Y-%m-%d")
    except Exception:
        return datetime.min


def matches_query(item, query):
    if not query:
        return True

    haystack = " ".join(
        [
            item.get("title", ""),
            item.get("author", ""),
            item.get("series", ""),
            item.get("topic", ""),
            str(item.get("sessionNumber", "")),
            item.get("description", ""),
            item.get("transcript", ""),
            " ".join(item.get("tags", [])),
        ]
    ).lower()

    return query.lower() in haystack


def drive_preview_url(file_id):
    return f"https://drive.google.com/file/d/{file_id}/preview"


def drive_download_url(file_id):
    return f"https://drive.google.com/uc?export=download&id={file_id}"


def ensure_defaults():
    st.session_state.setdefault("play", None)


catalog = load_json(CATALOG_PATH, [])
team = load_json(TEAM_PATH, {})
logo = find_logo()

st.set_page_config(page_title="ALBACAT v4.1", layout="wide")
ensure_defaults()

topics = sorted({x.get("topic", "") for x in catalog if x.get("topic")})
authors = sorted({x.get("author", "") for x in catalog if x.get("author")})
series_list = sorted({x.get("series", "") for x in catalog if x.get("series")})

with st.sidebar:
    safe_logo(logo, 150)
    st.title("ALBACAT v4.1")
    st.caption("Islamic History Audio Library")

    page = st.radio(
        "Navigate",
        [
            "Home",
            "Browse",
            "Series Playlist",
            "Now Playing",
            "Transcripts",
            "Analytics",
            "R&D Team",
            "About",
        ],
    )

    st.divider()
    st.markdown("**Google Drive setup**")
    st.caption("Share each file as: Anyone with the link → Viewer")

    st.divider()
    st.markdown("**Quick stats**")
    st.caption(f"Lectures: {len(catalog)}")
    st.caption(f"Series: {len(series_list)}")
    st.caption(f"Topics: {len(topics)}")
    st.caption(f"Authors: {len(authors)}")

safe_logo(logo, 180)
st.title("Project ALBACAT")
st.caption("Islamic history audio platform powered by Astrovia Systems")

contact = team.get("contact", {})
contact_parts = []
if contact.get("email"):
    contact_parts.append(f"Email: {contact['email']}")
if contact.get("phone"):
    contact_parts.append(f"Phone: {contact['phone']}")
if contact_parts:
    st.caption(" • ".join(contact_parts))


if page == "Home":
    st.subheader("Digital Library for Islamic History Audio")
    st.write(
        "Browse lectures, listen to organized series, search transcript text, "
        "and study Islamic history through a structured digital library."
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Lectures", len(catalog))
    m2.metric("Series", len(series_list))
    m3.metric("Topics", len(topics))
    m4.metric("Authors", len(authors))

    st.divider()
    st.subheader("Continue Listening")

    if st.session_state.get("play"):
        current = next((x for x in catalog if x.get("id") == st.session_state["play"]), None)
        if current:
            st.markdown(f"**{current.get('title')}**")
            st.write(current.get("description", ""))
            if st.button("Resume Lecture"):
                st.session_state["page_jump"] = "Now Playing"
                st.rerun()
    else:
        st.info("No lecture selected yet.")

    st.divider()
    st.subheader("Featured Series")

    if not series_list:
        st.info("No series available yet.")
    else:
        for series in series_list:
            items = [x for x in catalog if x.get("series") == series]
            items.sort(key=lambda x: x.get("sessionNumber", 0))
            if not items:
                continue

            first = items[0]
            st.markdown(
                f"**{series}**  \n"
                f"{first.get('author', '')} • {first.get('topic', '')} • {len(items)} session(s)"
            )


elif page == "Browse":
    st.subheader("Browse Catalog")

    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])

    with c1:
        q = st.text_input("Search", placeholder="title, topic, series, transcript...")
    with c2:
        selected_topic = st.selectbox("Topic", ["All"] + topics)
    with c3:
        selected_author = st.selectbox("Author", ["All"] + authors)
    with c4:
        selected_series = st.selectbox("Series", ["All"] + series_list)

    sort_by = st.selectbox("Sort", ["Newest", "Series → Session", "A–Z"])

    items = []
    for item in catalog:
        if selected_topic != "All" and item.get("topic") != selected_topic:
            continue
        if selected_author != "All" and item.get("author") != selected_author:
            continue
        if selected_series != "All" and item.get("series") != selected_series:
            continue
        if not matches_query(item, q):
            continue
        items.append(item)

    if sort_by == "Newest":
        items.sort(key=lambda x: parse_date(x.get("date", "")), reverse=True)
    elif sort_by == "Series → Session":
        items.sort(key=lambda x: (x.get("series", ""), x.get("sessionNumber", 0)))
    else:
        items.sort(key=lambda x: x.get("title", ""))

    st.write(f"**{len(items)}** item(s) found")

    cols = st.columns(3, gap="large")
    for i, item in enumerate(items):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"#### {item.get('title', 'Untitled')}")
                st.caption(
                    f"{item.get('author', '')} • {item.get('series', '')} • Topic: {item.get('topic', '')}"
                )
                st.markdown(
                    f"**Session:** #{item.get('sessionNumber', '—')}  \n"
                    f"**Duration:** {item.get('duration', '—')}  \n"
                    f"**Language:** {item.get('language', 'English')}  \n"
                    f"**Date:** {item.get('date', '—')}"
                )

                if item.get("description"):
                    st.write(item.get("description"))

                if item.get("tags"):
                    st.caption("Tags: " + ", ".join(item.get("tags", [])))

                b1, b2 = st.columns(2)
                with b1:
                    if st.button("▶ Play", key=f"play-{item['id']}"):
                        st.session_state["play"] = item["id"]
                        st.rerun()
                with b2:
                    st.link_button("⬇ Download", drive_download_url(item["fileId"]))


elif page == "Series Playlist":
    st.subheader("Series Playlist")

    if not series_list:
        st.info("No series available.")
    else:
        selected_series = st.selectbox("Select series", series_list)
        items = [x for x in catalog if x.get("series") == selected_series]
        items.sort(key=lambda x: x.get("sessionNumber", 0))

        if items:
            first = items[0]
            st.markdown(
                f"**{selected_series}**  \n"
                f"{first.get('author', '')} • {first.get('topic', '')} • {len(items)} session(s)"
            )

        st.divider()

        for item in items:
            with st.container(border=True):
                left, right = st.columns([3, 1])
                with left:
                    st.markdown(
                        f"**Session {item.get('sessionNumber', '—')}:** {item.get('title')}"
                    )
                    st.caption(
                        f"Duration: {item.get('duration', '—')} • Date: {item.get('date', '—')}"
                    )
                    if item.get("description"):
                        st.write(item.get("description"))
                with right:
                    if st.button("▶ Play", key=f"playlist-{item['id']}"):
                        st.session_state["play"] = item["id"]
                        st.rerun()
                    st.link_button("⬇ Download", drive_download_url(item["fileId"]))


elif page == "Now Playing":
    st.subheader("Now Playing")

    play_id = st.session_state.get("play")
    if not play_id:
        st.info("Pick a lecture from Browse or Series Playlist.")
    else:
        item = next((x for x in catalog if x.get("id") == play_id), None)

        if not item:
            st.warning("Selected lecture not found.")
        else:
            same_series = [x for x in catalog if x.get("series") == item.get("series")]
            same_series.sort(key=lambda x: x.get("sessionNumber", 0))
            ids = [x.get("id") for x in same_series]
            idx = ids.index(play_id)

            prev_id = ids[idx - 1] if idx > 0 else None
            next_id = ids[idx + 1] if idx < len(ids) - 1 else None

            top1, top2 = st.columns([3, 1])
            with top1:
                st.markdown(f"#### {item.get('title')}")
                st.caption(
                    f"{item.get('author', '')} • {item.get('series', '')} • "
                    f"Topic: {item.get('topic', '')} • Session #{item.get('sessionNumber', '—')}"
                )
            with top2:
                st.link_button("⬇ Download", drive_download_url(item["fileId"]))

            nav1, nav2, nav3 = st.columns(3)
            with nav1:
                if st.button("⟵ Previous", disabled=prev_id is None):
                    st.session_state["play"] = prev_id
                    st.rerun()
            with nav2:
                if st.button("Next ⟶", disabled=next_id is None):
                    st.session_state["play"] = next_id
                    st.rerun()
            with nav3:
                if st.button("View Transcript"):
                    st.session_state["page_jump"] = "Transcripts"
                    st.rerun()

            st.divider()
            st.components.v1.iframe(drive_preview_url(item["fileId"]), height=520)
            st.caption("Playback uses the Google Drive preview player for reliable streaming.")


elif page == "Transcripts":
    st.subheader("Lecture Transcripts")

    tq = st.text_input("Search transcript text", placeholder="Search inside transcript text...")

    filtered = catalog
    if tq:
        filtered = [
            x for x in catalog if tq.lower() in x.get("transcript", "").lower()
        ]

    if st.session_state.get("play"):
        current = next((x for x in catalog if x.get("id") == st.session_state["play"]), None)
        if current:
            st.info(f"Currently selected lecture: {current.get('title')}")

    for item in filtered:
        with st.container(border=True):
            st.markdown(f"### {item.get('title')}")
            if item.get("transcript"):
                st.write(item.get("transcript"))
            else:
                st.write("No transcript yet.")

            if st.button("Play this lecture", key=f"transcript-play-{item['id']}"):
                st.session_state["play"] = item["id"]
                st.rerun()


elif page == "Analytics":
    st.subheader("Analytics")
    st.write("Analytics dashboard coming soon.")


elif page == "R&D Team":
    st.subheader(team.get("team_name", "Research & Development Team"))

    if team.get("mission"):
        st.write(team.get("mission"))

    if team.get("contact"):
        st.markdown("#### Contact")
        if team["contact"].get("email"):
            st.write(f"**Email:** {team['contact']['email']}")
        if team["contact"].get("phone"):
            st.write(f"**Phone:** {team['contact']['phone']}")

    members = team.get("members", [])
    if members:
        cols = st.columns(2, gap="large")
        for i, member in enumerate(members):
            with cols[i % 2]:
                with st.container(border=True):
                    st.markdown(f"#### {member.get('name', 'Unnamed Member')}")
                    st.caption(member.get("role", ""))
                    if member.get("organization"):
                        st.caption(member.get("organization"))
                    if member.get("bio"):
                        st.write(member.get("bio"))
    else:
        st.info("No team members added yet.")


elif page == "About":
    st.subheader("About Project ALBACAT")
    st.write(
        "Project ALBACAT is a digital Islamic history audio platform designed to make "
        "lecture series easier to discover, stream, preserve, and study."
    )
    st.markdown(
        "- Home dashboard\n"
        "- Browse catalog\n"
        "- Series playlist page\n"
        "- Now Playing page\n"
        "- Transcript viewer\n"
        "- Analytics placeholder\n"
        "- R&D Team page"
                 )
