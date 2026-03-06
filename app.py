import json
from datetime import datetime
from typing import Dict, List, Optional

import streamlit as st

st.set_page_config(page_title="Project ALBACAT v2.1", layout="wide")

CATALOG_PATH = "catalog.json"


def load_catalog() -> List[Dict]:
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
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


def parse_date(s: str) -> datetime:
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except Exception:
        return datetime.min


def matches_query(item: Dict, q: str) -> bool:
    if not q:
        return True
    hay = "  ".join([
        item.get("title", ""),
        item.get("author", ""),
        item.get("series", ""),
        item.get("topic", ""),
        str(item.get("sessionNumber", "")),
        " ".join(item.get("tags") or []),
        item.get("description", ""),
    ]).lower()
    return q.lower() in hay.lower()


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


def next_prev_ids(catalog: List[Dict], current: Dict):
    items = series_items(catalog, current.get("series", ""))
    ids = [x.get("id") for x in items]
    if current.get("id") not in ids:
        return None, None
    idx = ids.index(current.get("id"))
    prev_id = ids[idx - 1] if idx > 0 else None
    next_id = ids[idx + 1] if idx < len(ids) - 1 else None
    return prev_id, next_id


ensure_defaults()
catalog = load_catalog()

topics = sorted({x.get("topic", "") for x in catalog if x.get("topic")})
authors = sorted({x.get("author", "") for x in catalog if x.get("author")})
series_list = sorted({x.get("series", "") for x in catalog if x.get("series")})

with st.sidebar:
    st.title("ALBACAT v2.1")
    st.caption("History Audio Library")

    page = st.radio(
        "Navigate",
        ["Home", "Browse", "Series Playlist", "Now Playing"],
        index=["Home", "Browse", "Series Playlist", "Now Playing"].index(st.session_state.page),
    )
    st.session_state.page = page

    st.divider()
    st.markdown("**Google Drive setup**")
    st.caption("Share each file as: Anyone with the link → Viewer")

st.markdown("## Project ALBACAT")
st.caption("Store-style catalog • Stable Google Drive preview playback • Series playlists")

if st.session_state.page == "Home":
    left, right = st.columns([2, 1], gap="large")

    with left:
        st.markdown("### Featured Series")
        if not series_list:
            st.info("No series found in catalog.json yet.")
        else:
            for s in series_list:
                items = series_items(catalog, s)
                topic = items[0].get("topic", "") if items else ""
                author = items[0].get("author", "") if items else ""

                st.markdown(f"**{s}**  \n{author} • {topic} • {len(items)} session(s)")

                b1, _ = st.columns([1, 2])
                with b1:
                    if st.button("Open playlist", key=f"openpl-{s}"):
                        st.session_state.selected_series = s
                        st.session_state.page = "Series Playlist"
                        st.rerun()

    with right:
        st.markdown("### Recently Added")
        recent = sorted(catalog, key=lambda x: parse_date(x.get("date", "")), reverse=True)[:6]
        for x in recent:
            st.write(f"• {x.get('title')}")

    st.divider()
    st.markdown("### Quick Start")
    st.markdown(
        "- Go to **Browse** to search and filter.\n"
        "- Go to **Series Playlist** for a lecture-by-lecture view.\n"
        "- Use **Now Playing** to open the player."
    )

elif st.session_state.page == "Browse":
    st.markdown("### Browse Catalog")

    c1, c2, c3, c4 = st.columns([2, 1, 1, 1], gap="medium")
    with c1:
        q = st.text_input("Search", placeholder="title, topic, series, tags…")
    with c2:
        t = st.selectbox("Topic", ["All"] + topics)
    with c3:
        a = st.selectbox("Author", ["All"] + authors)
    with c4:
        s = st.selectbox("Series", ["All"] + series_list)

    sort = st.selectbox("Sort", ["Newest", "Series → Session", "A–Z"])

    items = []
    for x in catalog:
        if t != "All" and x.get("topic") != t:
            continue
        if a != "All" and x.get("author") != a:
            continue
        if s != "All" and x.get("series") != s:
            continue
        if not matches_query(x, q):
            continue
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
            with st.container(border=True):
                st.markdown(f"#### {item.get('title', 'Untitled')}")
                st.caption(f"{item.get('author', '')} • {item.get('series', '')} • Topic: {item.get('topic', '')}")
                st.markdown(
                    f"**Session:** #{item.get('sessionNumber', '—')}  \n"
                    f"**Duration:** {item.get('duration', '—')}  \n"
                    f"**Language:** {item.get('language', 'English')}  \n"
                    f"**Date:** {item.get('date', '—')}"
                )
                if item.get("description"):
                    st.write(item.get("description"))

                b1, b2 = st.columns(2)
                with b1:
                    if st.button("▶ Play", key=f"play-{item['id']}"):
                        pick_item(catalog, item["id"])
                        st.session_state.page = "Now Playing"
                        st.rerun()
                with b2:
                    st.link_button("⬇ Download", drive_download_url(item["fileId"]))

elif st.session_state.page == "Series Playlist":
    st.markdown("### Series Playlist")

    if not series_list:
        st.info("No series available.")
    else:
        if not st.session_state.selected_series:
            st.session_state.selected_series = series_list[0]

        chosen = st.selectbox(
            "Select series",
            series_list,
            index=series_list.index(st.session_state.selected_series) if st.session_state.selected_series in series_list else 0,
        )
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
                    left, right = st.columns([3, 1], gap="medium")
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

        top1, top2 = st.columns([3, 1], gap="large")
        with top1:
            st.markdown(f"#### {sel.get('title')}")
            st.caption(
                f"{sel.get('author', '')} • {sel.get('series', '')} • "
                f"Topic: {sel.get('topic', '')} • Session #{sel.get('sessionNumber', '—')}"
            )
        with top2:
            st.link_button("⬇ Download", drive_download_url(sel["fileId"]))

        nav1, nav2, nav3 = st.columns([1, 1, 2], gap="medium")
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
        st.caption("This version uses the Google Drive preview player directly for more reliable playback.")
