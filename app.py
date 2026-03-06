import base64
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import requests
import streamlit as st

st.set_page_config(page_title="Project ALBACAT v2", layout="wide")

CATALOG_PATH = "catalog.json"
MAX_BASE64_BYTES = 10 * 1024 * 1024  # 10MB


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


def safe_lower(x) -> str:
    return str(x or "").lower()


def matches_query(item: Dict, q: str) -> bool:
    if not q:
        return True
    hay = "  ".join(
        [
            item.get("title", ""),
            item.get("author", ""),
            item.get("series", ""),
            item.get("topic", ""),
            str(item.get("sessionNumber", "")),
            " ".join(item.get("tags") or []),
            item.get("description", ""),
        ]
    ).lower()
    return q.lower() in hay


def drive_download_url(file_id: str) -> str:
    return f"https://drive.google.com/uc?export=download&id={file_id}"


def drive_preview_url(file_id: str) -> str:
    return f"https://drive.google.com/file/d/{file_id}/preview"


def drive_open_url(file_id: str) -> str:
    return f"https://drive.google.com/file/d/{file_id}/view"


def slugify(s: str) -> str:
    s = safe_lower(s).strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


@st.cache_data(show_spinner=False, ttl=3600)
def fetch_drive_audio_bytes(file_id: str) -> Tuple[Optional[bytes], Optional[str]]:
    url = drive_download_url(file_id)
    sess = requests.Session()
    try:
        r = sess.get(url, stream=True, timeout=40)
    except Exception as e:
        return None, f"Network error: {e}"

    ct = (r.headers.get("Content-Type") or "").lower()

    if "text/html" in ct:
        try:
            html = r.text
        except Exception:
            return None, "Drive returned HTML and couldn’t be parsed."

        m = re.search(r"confirm=([0-9A-Za-z_]+)", html)
        if not m:
            return None, (
                "Drive didn’t return a direct file. "
                "Check sharing: Anyone with link (Viewer). "
                "If it’s very large, Drive may require confirmation."
            )

        confirm = m.group(1)
        url2 = drive_download_url(file_id) + f"&confirm={confirm}"
        try:
            r2 = sess.get(url2, stream=True, timeout=60)
        except Exception as e:
            return None, f"Network error after confirm: {e}"

        ct2 = (r2.headers.get("Content-Type") or "").lower()
        if "text/html" in ct2:
            return None, "Drive still returned HTML after confirmation. Try smaller file or different sharing."
        return r2.content, None

    try:
        return r.content, None
    except Exception as e:
        return None, f"Could not read content: {e}"


def audio_player_with_speed(audio_bytes: bytes, mime: str = "audio/mpeg", rate: float = 1.0):
    b64 = base64.b64encode(audio_bytes).decode("utf-8")
    html = f'''
    <div style="padding:12px;border-radius:16px;border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.04)">
      <audio id="albacat_audio" controls style="width:100%">
        <source src="data:{mime};base64,{b64}" type="{mime}">
        Your browser does not support the audio element.
      </audio>
      <script>
        const a = document.getElementById("albacat_audio");
        if (a) {{
          a.playbackRate = {rate};
        }}
      </script>
      <div style="margin-top:8px;color:rgba(255,255,255,.75);font-size:12px;">
        Speed is set to <b>{rate}×</b>. Use the speed selector to change it.
      </div>
    </div>
    '''
    st.components.v1.html(html, height=130)


def ensure_session_defaults():
    st.session_state.setdefault("page", "Home")
    st.session_state.setdefault("selected_id", None)
    st.session_state.setdefault("selected_series", None)
    st.session_state.setdefault("speed", 1.0)


def pick_item(catalog: List[Dict], item_id: str):
    st.session_state.selected_id = item_id
    item = next((x for x in catalog if x.get("id") == item_id), None)
    if item:
        st.session_state.selected_series = item.get("series")


def get_selected_item(catalog: List[Dict]) -> Optional[Dict]:
    sid = st.session_state.get("selected_id")
    if not sid:
        return None
    return next((x for x in catalog if x.get("id") == sid), None)


def series_items(catalog: List[Dict], series_name: str) -> List[Dict]:
    items = [x for x in catalog if x.get("series") == series_name]
    items.sort(key=lambda x: (x.get("sessionNumber", 0), x.get("title", "")))
    return items


def next_prev_ids(catalog: List[Dict], current: Dict) -> Tuple[Optional[str], Optional[str]]:
    s = current.get("series", "")
    if not s:
        return None, None
    items = series_items(catalog, s)
    ids = [x["id"] for x in items]
    try:
        i = ids.index(current["id"])
    except ValueError:
        return None, None
    prev_id = ids[i - 1] if i - 1 >= 0 else None
    next_id = ids[i + 1] if i + 1 < len(ids) else None
    return prev_id, next_id


ensure_session_defaults()
catalog = load_catalog()

topics = sorted({x.get("topic", "") for x in catalog if x.get("topic")})
series_list = sorted({x.get("series", "") for x in catalog if x.get("series")})
authors = sorted({x.get("author", "") for x in catalog if x.get("author")})

with st.sidebar:
    st.title("ALBACAT v2")
    st.caption("History Audio Library")

    page = st.radio(
        "Navigate",
        ["Home", "Browse", "Series Playlist", "Now Playing"],
        index=["Home", "Browse", "Series Playlist", "Now Playing"].index(st.session_state.page),
    )
    st.session_state.page = page

    st.divider()
    st.subheader("Player")
    st.session_state.speed = st.select_slider(
        "Playback speed",
        options=[0.75, 1.0, 1.25, 1.5, 1.75, 2.0],
        value=st.session_state.speed,
    )

    st.divider()
    st.markdown("**Google Drive tip**")
    st.caption("Set each audio to: Anyone with the link → Viewer")

st.markdown("## Project ALBACAT")
st.caption("Store-style catalog • Reliable Drive playback • Series playlists")

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
                st.markdown(f"**{s}**  
{author} • {topic} • {len(items)} session(s)")
                b1, _ = st.columns([1, 2])
                with b1:
                    if st.button("Open playlist", key=f"openpl-{slugify(s)}"):
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
        "- Go to **Browse** to search and filter.
"
        "- Go to **Series Playlist** for a lecture-by-lecture view.
"
        "- Use **Now Playing** for player + next/prev."
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
        col = cols[i % 3]
        with col:
            with st.container(border=True):
                st.markdown(f"#### {item.get('title','Untitled')}")
                st.caption(f"{item.get('author','')} • {item.get('series','')} • Topic: {item.get('topic','')}")
                st.markdown(
                    f"**Session:** #{item.get('sessionNumber','—')}  
"
                    f"**Duration:** {item.get('duration','—')}  
"
                    f"**Language:** {item.get('language','English')}  
"
                    f"**Date:** {item.get('date','—')}"
                )
                if item.get("description"):
                    st.write(item["description"])

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

    if not st.session_state.selected_series:
        st.session_state.selected_series = series_list[0] if series_list else None

    if not series_list:
        st.info("No series available.")
    else:
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
            st.markdown(f"**{chosen}**  
{author} • {topic} • {len(items)} sessions")

            st.divider()

            for item in items:
                row = st.container(border=True)
                with row:
                    left, right = st.columns([3, 1], gap="medium")
                    with left:
                        st.markdown(f"**Session {item.get('sessionNumber','—')}:** {item.get('title')}")
                        st.caption(f"Duration: {item.get('duration','—')} • Date: {item.get('date','—')}")
                        if item.get("description"):
                            st.write(item["description"])
                    with right:
                        if st.button("▶ Play", key=f"pl-{item['id']}"):
                            pick_item(catalog, item["id"])
                            st.session_state.page = "Now Playing"
                            st.rerun()
                        st.link_button("⬇ Download", drive_download_url(item["fileId"]))
                        st.link_button("↗ Open in Drive", drive_open_url(item["fileId"]))

elif st.session_state.page == "Now Playing":
    st.markdown("### Now Playing")

    sel = get_selected_item(catalog)
    if not sel:
        st.info("Pick a session from **Browse** or **Series Playlist**.")
    else:
        prev_id, next_id = next_prev_ids(catalog, sel)

        top1, top2 = st.columns([3, 1], gap="large")
        with top1:
            st.markdown(f"#### {sel.get('title')}")
            st.caption(
                f"{sel.get('author','')} • {sel.get('series','')} • "
                f"Topic: {sel.get('topic','')} • Session #{sel.get('sessionNumber','—')}"
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
            st.caption(f"Speed: **{st.session_state.speed}×**")

        st.divider()

        with st.spinner("Loading audio…"):
            audio_bytes, err = fetch_drive_audio_bytes(sel["fileId"])

        if err or not audio_bytes:
            st.warning(
                f"Couldn’t load audio bytes directly.\n\n"
                f"**Reason:** {err or 'Unknown'}\n\n"
                f"Using Google Drive preview fallback below (still works reliably)."
            )
            st.components.v1.iframe(drive_preview_url(sel["fileId"]), height=520)
            st.link_button("↗ Open in Drive", drive_open_url(sel["fileId"]))
        else:
            if len(audio_bytes) <= MAX_BASE64_BYTES:
                audio_player_with_speed(audio_bytes, mime="audio/mpeg", rate=float(st.session_state.speed))
            else:
                st.audio(audio_bytes, format="audio/mpeg")
                st.caption("Speed control is limited for large files in this mode.")
                with st.expander("Open Drive preview player (fallback)"):
                    st.components.v1.iframe(drive_preview_url(sel["fileId"]), height=520)
                    st.link_button("↗ Open in Drive", drive_open_url(sel["fileId"]))
