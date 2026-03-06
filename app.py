import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import streamlit as st

st.set_page_config(page_title="Project ALBACAT v3.1", layout="wide")

CATALOG_PATH = "catalog.json"
TEAM_PATH = "team.json"

def load_json(path: str, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def load_catalog() -> List[Dict]:
    data = load_json(CATALOG_PATH, [])
    for x in data:
        x.setdefault("tags", [])
        x.setdefault("topic", "")
        x.setdefault("series", "")
        x.setdefault("author", "")
        x.setdefault("language", "English")
        x.setdefault("sessionNumber", 0)
        x.setdefault("date", "")
        x.setdefault("duration", "")
        x.setdefault("description", "")
    return data

def load_team() -> Dict:
    return load_json(TEAM_PATH, {"team_name": "Project ALBACAT Research & Development Team", "mission": "", "contact": {}, "organization": {}, "members": []})

def parse_date(s: str) -> datetime:
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except Exception:
        return datetime.min

def matches_query(item: Dict, q: str) -> bool:
    if not q:
        return True
    hay = "  ".join([item.get("title", ""), item.get("author", ""), item.get("series", ""), item.get("topic", ""), str(item.get("sessionNumber", "")), " ".join(item.get("tags") or []), item.get("description", "")]).lower()
    return q.lower() in hay

def drive_preview_url(file_id: str) -> str:
    return f"https://drive.google.com/file/d/{file_id}/preview"

def drive_download_url(file_id: str) -> str:
    return f"https://drive.google.com/uc?export=download&id={file_id}"

def drive_open_url(file_id: str) -> str:
    return f"https://drive.google.com/file/d/{file_id}/view"

def ensure_defaults():
    st.session_state.setdefault("page", "Home")
    st.session_state.setdefault("selected_id", None)
    st.session_state.setdefault("selected_series", None)

def get_item_by_id(catalog: List[Dict], item_id: Optional[str]) -> Optional[Dict]:
    if not item_id:
        return None
    for item in catalog:
        if item.get("id") == item_id:
            return item
    return None

def pick_item(catalog: List[Dict], item_id: str):
    st.session_state.selected_id = item_id
    item = get_item_by_id(catalog, item_id)
    if item:
        st.session_state.selected_series = item.get("series")

def series_items(catalog: List[Dict], series_name: str) -> List[Dict]:
    items = [x for x in catalog if x.get("series") == series_name]
    items.sort(key=lambda x: (x.get("sessionNumber", 0), x.get("title", "")))
    return items

def next_prev_ids(catalog: List[Dict], current: Dict) -> Tuple[Optional[str], Optional[str]]:
    items = series_items(catalog, current.get("series", ""))
    ids = [x.get("id") for x in items]
    if current.get("id") not in ids:
        return None, None
    idx = ids.index(current.get("id"))
    prev_id = ids[idx - 1] if idx > 0 else None
    next_id = ids[idx + 1] if idx < len(ids) - 1 else None
    return prev_id, next_id

def get_logo_path(team: Dict):
    candidate = team.get("organization", {}).get("logo", "logo.png")
    return candidate if candidate and os.path.exists(candidate) else None

def render_card(item: Dict, catalog: List[Dict], show_open_drive: bool = False):
    with st.container(border=True):
        st.markdown(f"#### {item.get('title', 'Untitled')}")
        st.caption(f"{item.get('author', '')} • {item.get('series', '')} • Topic: {item.get('topic', '')}")
        st.markdown(f"**Session:** #{item.get('sessionNumber', '—')}  \n**Duration:** {item.get('duration', '—')}  \n**Language:** {item.get('language', 'English')}  \n**Date:** {item.get('date', '—')}")
        if item.get("description"):
            st.write(item.get("description"))
        if item.get("tags"):
            st.caption("Tags: " + ", ".join(item.get("tags")))
        c1, c2 = st.columns(2)
        with c1:
            if st.button("▶ Play", key=f"play-{item['id']}"):
                pick_item(catalog, item["id"])
                st.session_state.page = "Now Playing"
                st.rerun()
        with c2:
            st.link_button("⬇ Download", drive_download_url(item["fileId"]))
        if show_open_drive:
            st.link_button("↗ Open in Drive", drive_open_url(item["fileId"]))

ensure_defaults()
catalog = load_catalog()
team = load_team()
logo_path = get_logo_path(team)
topics = sorted({x.get("topic", "") for x in catalog if x.get("topic")})
authors = sorted({x.get("author", "") for x in catalog if x.get("author")})
series_list = sorted({x.get("series", "") for x in catalog if x.get("series")})
with st.sidebar:
    if logo_path:
        st.image(logo_path, width=190)
    st.title("ALBACAT v3.1")
    st.caption("Islamic History Audio Library")
    page = st.radio("Navigate", ["Home", "Browse", "Series Playlist", "Now Playing", "R&D Team", "About"], index=["Home", "Browse", "Series Playlist", "Now Playing", "R&D Team", "About"].index(st.session_state.page))
    st.session_state.page = page
    st.divider()
    st.markdown("**Google Drive setup**")
    st.caption("Share each file as: Anyone with the link → Viewer")
    st.divider()
    st.markdown("**Quick stats**")
    st.caption(f"Lectures: {len(catalog)}")
    st.caption(f"Series: {len(series_list)}")
    st.caption(f"Topics: {len(topics)}")
header_left, header_right = st.columns([3,1], gap="large")
with header_left:
    st.markdown("## Project ALBACAT")
    st.caption("ALBACAT v3.1 • Store-style catalog • Series playlists • Research & Development team profile")
with header_right:
    if logo_path:
        st.image(logo_path, width=170)
if st.session_state.page == "Home":
    hero_left, hero_right = st.columns([2,1], gap="large")
    with hero_left:
        st.markdown("### Digital Library for Islamic History Audio")
        st.write("Project ALBACAT organizes Islamic history lectures into a structured listening library. Users can browse by series, topic, and session, then play or download each lecture from Google Drive.")
        s1, s2, s3 = st.columns(3)
        s1.metric("Lectures", len(catalog))
        s2.metric("Series", len(series_list))
        s3.metric("Authors", len(authors))
    with hero_right:
        st.markdown("### Research & Development")
        st.write(team.get("mission", ""))
        contact = team.get("contact", {})
        if contact.get("email"):
            st.caption(f"Email: {contact.get('email')}")
        if contact.get("phone"):
            st.caption(f"Phone: {contact.get('phone')}")
        if st.button("View team information"):
            st.session_state.page = "R&D Team"
            st.rerun()
    st.divider()
    st.markdown("### Featured Series")
    if not series_list:
        st.info("No series found in catalog.json yet.")
    else:
        for s in series_list:
            items = series_items(catalog, s)
            topic = items[0].get("topic", "") if items else ""
            author = items[0].get("author", "") if items else ""
            st.markdown(f"**{s}**  \n{author} • {topic} • {len(items)} session(s)")
            b1, _ = st.columns([1,4])
            with b1:
                if st.button("Open playlist", key=f"home-series-{s}"):
                    st.session_state.selected_series = s
                    st.session_state.page = "Series Playlist"
                    st.rerun()
    st.divider()
    st.markdown("### Recently Added")
    recent = sorted(catalog, key=lambda x: parse_date(x.get("date", "")), reverse=True)[:3]
    cols = st.columns(3, gap="large")
    for i, item in enumerate(recent):
        with cols[i % 3]:
            render_card(item, catalog)
elif st.session_state.page == "Browse":
    st.markdown("### Browse Catalog")
    c1, c2, c3, c4 = st.columns([2,1,1,1], gap="medium")
    with c1:
        q = st.text_input("Search", placeholder="title, topic, series, tags…")
    with c2:
        t = st.selectbox("Topic", ["All"] + topics)
    with c3:
        a = st.selectbox("Author", ["All"] + authors)
    with c4:
        s = st.selectbox("Series", ["All"] + series_list)
    sort = st.selectbox("Sort", ["Newest", "Series → Session", "A–Z"])
    items=[]
    for x in catalog:
        if t != "All" and x.get("topic") != t: continue
        if a != "All" and x.get("author") != a: continue
        if s != "All" and x.get("series") != s: continue
        if not matches_query(x, q): continue
        items.append(x)
    if sort == "Newest":
        items.sort(key=lambda x: parse_date(x.get("date", "")), reverse=True)
    elif sort == "Series → Session":
        items.sort(key=lambda x: (x.get("series", ""), x.get("sessionNumber", 0)))
    else:
        items.sort(key=lambda x: x.get("title", ""))
    st.write(f"**{len(items)}** item(s)")
    cols = st.columns(3, gap="large")
    for i, item in enumerate(items):
        with cols[i % 3]:
            render_card(item, catalog)
elif st.session_state.page == "Series Playlist":
    st.markdown("### Series Playlist")
    if not series_list:
        st.info("No series available.")
    else:
        if not st.session_state.selected_series:
            st.session_state.selected_series = series_list[0]
        chosen = st.selectbox("Select series", series_list, index=series_list.index(st.session_state.selected_series) if st.session_state.selected_series in series_list else 0)
        st.session_state.selected_series = chosen
        items = series_items(catalog, chosen)
        if not items:
            st.info("No sessions found for this series.")
        else:
            author = items[0].get("author", "")
            topic = items[0].get("topic", "")
            st.markdown(f"**{chosen}**  \n{author} • {topic} • {len(items)} session(s)")
            st.divider()
            for item in items:
                with st.container(border=True):
                    left, right = st.columns([3,1], gap="medium")
                    with left:
                        st.markdown(f"**Session {item.get('sessionNumber', '—')}:** {item.get('title')}")
                        st.caption(f"Duration: {item.get('duration', '—')} • Date: {item.get('date', '—')}")
                        if item.get("description"):
                            st.write(item.get("description"))
                    with right:
                        if st.button("▶ Play", key=f"playlist-{item['id']}"):
                            pick_item(catalog, item["id"])
                            st.session_state.page = "Now Playing"
                            st.rerun()
                        st.link_button("⬇ Download", drive_download_url(item["fileId"]))
                        st.link_button("↗ Open in Drive", drive_open_url(item["fileId"]))
elif st.session_state.page == "Now Playing":
    st.markdown("### Now Playing")
    sel = get_item_by_id(catalog, st.session_state.selected_id)
    if not sel:
        st.info("Pick a session from **Browse** or **Series Playlist**.")
    else:
        prev_id, next_id = next_prev_ids(catalog, sel)
        top1, top2 = st.columns([3,1], gap="large")
        with top1:
            st.markdown(f"#### {sel.get('title')}")
            st.caption(f"{sel.get('author', '')} • {sel.get('series', '')} • Topic: {sel.get('topic', '')} • Session #{sel.get('sessionNumber', '—')}")
        with top2:
            st.link_button("⬇ Download", drive_download_url(sel["fileId"]))
        nav1, nav2, nav3 = st.columns([1,1,2], gap="medium")
        with nav1:
            if st.button("⟵ Previous", disabled=prev_id is None):
                pick_item(catalog, prev_id)
                st.rerun()
        with nav2:
            if st.button("Next ⟶", disabled=next_id is None):
                pick_item(catalog, next_id)
                st.rerun()
        with nav3:
            st.link_button("↗ Open in Drive", drive_open_url(sel["fileId"]))
        st.divider()
        st.components.v1.iframe(drive_preview_url(sel["fileId"]), height=520)
        st.caption("Playback uses the Google Drive preview player for reliable streaming.")
elif st.session_state.page == "R&D Team":
    if logo_path:
        st.image(logo_path, width=220)
    st.markdown(f"### {team.get('team_name', 'Research & Development Team')}")
    if team.get("mission"):
        st.write(team.get("mission"))
    contact = team.get("contact", {})
    if contact.get("email") or contact.get("phone"):
        st.markdown("#### Contact")
        if contact.get("email"):
            st.write(f"Email: {contact.get('email')}")
        if contact.get("phone"):
            st.write(f"Phone: {contact.get('phone')}")
    members = team.get("members", [])
    if not members:
        st.info("No team members added yet. Edit team.json to add them.")
    else:
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
                    if member.get("email"):
                        st.caption(f"Email: {member.get('email')}")
                    if member.get("phone"):
                        st.caption(f"Phone: {member.get('phone')}")
    st.divider()
    st.caption("Edit team.json anytime to update your research and development team information.")
else:
    st.markdown("### About Project ALBACAT")
    st.write("Project ALBACAT is a digital catalog for Islamic history audio content. It is designed to make lecture series easier to discover, stream, and preserve.")
    st.markdown("### Included in v3.1")
    st.markdown("- Home dashboard\n- Browse catalog\n- Series playlist page\n- Now Playing page\n- Research & Development Team page\n- Contact information\n- Logo support via logo.png\n- Editable catalog.json and team.json")
