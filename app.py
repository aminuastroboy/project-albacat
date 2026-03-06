import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import streamlit as st

st.set_page_config(page_title="Project ALBACAT v4", layout="wide")

CATALOG_PATH = "catalog.json"
TEAM_PATH = "team.json"
SAMPLE_CATALOG_PATH = "sample_catalog.json"
LOGO_CANDIDATES = ["logo.png", os.path.join("assets", "logo.png"), os.path.join("assets", "logo.jpg")]


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
        x.setdefault("cover", "")
        x.setdefault("transcript", "")
    return data


def load_team() -> Dict:
    return load_json(
        TEAM_PATH,
        {
            "team_name": "Project ALBACAT Research & Development Team",
            "mission": "",
            "contact": {},
            "organization": {},
            "members": [],
        },
    )


def parse_date(s: str) -> datetime:
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except Exception:
        return datetime.min


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
            item.get("transcript", ""),
        ]
    ).lower()
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
    st.session_state.setdefault("last_played", [])
    st.session_state.setdefault("play_counts", {})


def find_logo() -> Optional[str]:
    for path in LOGO_CANDIDATES:
        if os.path.exists(path):
            return path
    return None


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
        counts = dict(st.session_state.play_counts)
        counts[item_id] = counts.get(item_id, 0) + 1
        st.session_state.play_counts = counts

        history = list(st.session_state.last_played)
        history = [x for x in history if x != item_id]
        history.insert(0, item_id)
        st.session_state.last_played = history[:10]


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


def render_branding(logo_path: Optional[str], team: Dict):
    if logo_path:
        st.image(logo_path, width=180)
    st.markdown("## Project ALBACAT")
    st.caption("ALBACAT v4 • Islamic history audio platform • Astrovia Systems")
    contact = team.get("contact", {})
    if contact:
        parts = []
        if contact.get("email"):
            parts.append(f"Email: {contact['email']}")
        if contact.get("phone"):
            parts.append(f"Phone: {contact['phone']}")
        st.caption(" • ".join(parts))


def render_card(item: Dict, catalog: List[Dict], compact: bool = False):
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
            st.caption("Tags: " + ", ".join(item.get("tags")))

        c1, c2 = st.columns(2)
        with c1:
            if st.button("▶ Play", key=f"play-{item['id']}"):
                pick_item(catalog, item["id"])
                st.session_state.page = "Now Playing"
                st.rerun()
        with c2:
            st.link_button("⬇ Download", drive_download_url(item["fileId"]))

        if not compact:
            cols = st.columns(2)
            with cols[0]:
                st.link_button("↗ Open in Drive", drive_open_url(item["fileId"]))
            with cols[1]:
                if st.button("View transcript", key=f"transcript-{item['id']}"):
                    pick_item(catalog, item["id"])
                    st.session_state.page = "Transcripts"
                    st.rerun()


ensure_defaults()
catalog = load_catalog()
team = load_team()
sample_catalog = load_json(SAMPLE_CATALOG_PATH, [])
logo_path = find_logo()

topics = sorted({x.get("topic", "") for x in catalog if x.get("topic")})
authors = sorted({x.get("author", "") for x in catalog if x.get("author")})
series_list = sorted({x.get("series", "") for x in catalog if x.get("series")})

with st.sidebar:
    if logo_path:
        st.image(logo_path, width=150)
    st.title("ALBACAT v4")
    st.caption("Islamic History Audio Platform")

    page_options = [
        "Home",
        "Browse",
        "Series Playlist",
        "Now Playing",
        "Transcripts",
        "Analytics",
        "R&D Team",
        "Admin Guide",
        "About",
    ]
    page = st.radio("Navigate", page_options, index=page_options.index(st.session_state.page))
    st.session_state.page = page

    st.divider()
    st.markdown("**Google Drive setup**")
    st.caption("Share each file as: Anyone with the link → Viewer")

    st.divider()
    st.markdown("**Quick stats**")
    st.caption(f"Lectures: {len(catalog)}")
    st.caption(f"Series: {len(series_list)}")
    st.caption(f"Topics: {len(topics)}")
    st.caption(f"Authors: {len(authors)}")

render_branding(logo_path, team)

if st.session_state.page == "Home":
    hero_left, hero_right = st.columns([2, 1], gap="large")

    with hero_left:
        st.markdown("### Digital Library for Islamic History Audio")
        st.write(
            "Project ALBACAT organizes Islamic history lectures into a structured listening library. "
            "Browse by series, topic, scholar, and session, then stream or download each lecture from Google Drive."
        )
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Lectures", len(catalog))
        m2.metric("Series", len(series_list))
        m3.metric("Topics", len(topics))
        m4.metric("Authors", len(authors))

    with hero_right:
        st.markdown("### Research & Development")
        st.write(team.get("mission", ""))
        if st.button("Open R&D Team"):
            st.session_state.page = "R&D Team"
            st.rerun()

    st.divider()
    st.markdown("### Continue Listening")
    if st.session_state.last_played:
        items = [get_item_by_id(catalog, x) for x in st.session_state.last_played]
        items = [x for x in items if x]
        cols = st.columns(min(3, max(1, len(items))), gap="large")
        for i, item in enumerate(items[:3]):
            with cols[i % len(cols)]:
                render_card(item, catalog, compact=True)
    else:
        st.info("No listening history yet. Start a lecture and it will appear here.")

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
            c1, c2 = st.columns([1, 4])
            with c1:
                if st.button("Open playlist", key=f"home-series-{s}"):
                    st.session_state.selected_series = s
                    st.session_state.page = "Series Playlist"
                    st.rerun()
            with c2:
                st.caption("")

elif st.session_state.page == "Browse":
    st.markdown("### Browse Catalog")

    c1, c2, c3, c4 = st.columns([2, 1, 1, 1], gap="medium")
    with c1:
        q = st.text_input("Search", placeholder="title, topic, series, tags, transcript…")
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
            render_card(item, catalog)

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
            index=series_list.index(st.session_state.selected_series)
            if st.session_state.selected_series in series_list
            else 0,
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

        nav1, nav2, nav3, nav4 = st.columns([1, 1, 1, 2], gap="medium")
        with nav1:
            if st.button("⟵ Previous", disabled=prev_id is None):
                pick_item(catalog, prev_id)
                st.rerun()
        with nav2:
            if st.button("Next ⟶", disabled=next_id is None):
                pick_item(catalog, next_id)
                st.rerun()
        with nav3:
            if st.button("Transcript"):
                st.session_state.page = "Transcripts"
                st.rerun()
        with nav4:
            st.link_button("↗ Open in Drive", drive_open_url(sel["fileId"]))

        st.divider()
        st.components.v1.iframe(drive_preview_url(sel["fileId"]), height=520)
        st.caption("Playback uses the Google Drive preview player for reliable streaming.")

elif st.session_state.page == "Transcripts":
    st.markdown("### Lecture Transcripts & Summaries")
    sel = get_item_by_id(catalog, st.session_state.selected_id)
    if sel:
        st.info(f"Currently selected lecture: {sel.get('title')}")
        st.markdown(f"#### {sel.get('title')}")
        if sel.get("transcript"):
            st.write(sel.get("transcript"))
        else:
            st.warning("No transcript has been added for this lecture yet.")
    else:
        st.info("Select a lecture first to view its transcript.")

    st.divider()
    st.markdown("### Search Across Transcript Text")
    tq = st.text_input("Transcript search", placeholder="Search inside transcript text…")
    if tq:
        results = [x for x in catalog if tq.lower() in (x.get("transcript", "").lower())]
        st.write(f"**{len(results)}** result(s)")
        for item in results:
            with st.container(border=True):
                st.markdown(f"**{item.get('title')}**")
                excerpt = item.get("transcript", "")
                st.write(excerpt[:350] + ("..." if len(excerpt) > 350 else ""))
                if st.button("Open lecture", key=f"open-transcript-{item['id']}"):
                    pick_item(catalog, item["id"])
                    st.session_state.page = "Now Playing"
                    st.rerun()

elif st.session_state.page == "Analytics":
    st.markdown("### Analytics Dashboard")
    counts = st.session_state.play_counts
    total_plays = sum(counts.values())
    top_items = sorted(
        [(get_item_by_id(catalog, k), v) for k, v in counts.items() if get_item_by_id(catalog, k)],
        key=lambda x: x[1],
        reverse=True,
    )

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Plays", total_plays)
    m2.metric("Lectures Tracked", len(counts))
    m3.metric("Recent Listens", len(st.session_state.last_played))

    st.divider()
    st.markdown("### Most Played Lectures")
    if not top_items:
        st.info("No plays yet. Start listening and this dashboard will populate.")
    else:
        for item, plays in top_items:
            st.markdown(f"**{item.get('title')}** — {plays} play(s)")

    st.divider()
    st.markdown("### Listening History")
    if not st.session_state.last_played:
        st.info("No recent listening history yet.")
    else:
        for item_id in st.session_state.last_played:
            item = get_item_by_id(catalog, item_id)
            if item:
                st.write(f"• {item.get('title')}")

elif st.session_state.page == "R&D Team":
    st.markdown(f"### {team.get('team_name', 'Research & Development Team')}")
    if team.get("mission"):
        st.write(team.get("mission"))

    contact = team.get("contact", {})
    if contact:
        st.markdown("#### Contact")
        if contact.get("email"):
            st.write(f"**Email:** {contact.get('email')}")
        if contact.get("phone"):
            st.write(f"**Phone:** {contact.get('phone')}")

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

elif st.session_state.page == "Admin Guide":
    st.markdown("### Admin Guide")
    st.write(
        "ALBACAT v4 keeps administration simple by using editable JSON files. "
        "You can update lectures, transcripts, team data, and branding without changing the app logic."
    )

    st.markdown("#### Add a new lecture")
    st.code(load_json(SAMPLE_CATALOG_PATH, []), language="json")

    st.markdown("#### Update team details")
    st.write("Edit `team.json` to change members, email, phone, and organization info.")

    st.markdown("#### Add branding")
    st.write("Place your Astrovia Systems logo at the project root as `logo.png`, or in `assets/logo.png`.")

    st.markdown("#### Suggested next step for production")
    st.write(
        "Move from JSON files to a database and admin form when you start managing many scholars, "
        "many series, and frequent transcript updates."
    )

elif st.session_state.page == "About":
    st.markdown("### About Project ALBACAT")
    st.write(
        "Project ALBACAT is a digital Islamic history audio platform designed to make lecture series "
        "easier to discover, stream, preserve, and study."
    )
    st.markdown("### Included in v4")
    st.markdown(
        "- Home dashboard with continue listening\n"
        "- Browse catalog with search, filters, and sorting\n"
        "- Series playlist page\n"
        "- Now Playing page with next and previous controls\n"
        "- Transcript and summary page\n"
        "- Analytics dashboard\n"
        "- Research & Development Team page\n"
        "- Admin guide for content management\n"
        "- Editable `catalog.json`, `team.json`, and `sample_catalog.json`"
    )
