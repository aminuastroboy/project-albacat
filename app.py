
import json, os
import streamlit as st
from PIL import UnidentifiedImageError

CATALOG_PATH="catalog.json"
TEAM_PATH="team.json"

def load_json(p,d):
    try:
        with open(p,"r",encoding="utf-8") as f:
            return json.load(f)
    except:
        return d

def safe_logo(p,w):
    if not p: return
    try:
        st.image(p,width=w)
    except (UnidentifiedImageError,OSError):
        pass

def find_logo():
    for p in ["logo.png","assets/logo.png"]:
        if os.path.exists(p):
            return p
    return None

def drive_preview(id):
    return f"https://drive.google.com/file/d/{id}/preview"

catalog=load_json(CATALOG_PATH,[])
team=load_json(TEAM_PATH,{})
logo=find_logo()

st.set_page_config(page_title="ALBACAT v4.2",layout="wide")

if "play" not in st.session_state:
    st.session_state.play=None

with st.sidebar:
    safe_logo(logo,150)
    st.title("ALBACAT v4.2")

    page=st.radio("Navigate",[
        "Home","Search","Browse","Now Playing","Transcripts","Analytics","R&D Team","About"
    ])

safe_logo(logo,180)
st.title("Project ALBACAT")

contact=team.get("contact",{})
if contact:
    st.caption(f"{contact.get('email','')} • {contact.get('phone','')}")

# HOME
if page=="Home":
    st.subheader("Islamic History Audio Library")
    st.metric("Total Lectures",len(catalog))

# GLOBAL SEARCH
if page=="Search":
    q=st.text_input("Global Search","")
    results=[x for x in catalog if q.lower() in (x["title"]+x.get("transcript","")).lower()]
    for r in results:
        st.markdown("### "+r["title"])
        if st.button("Play "+r["id"]):
            st.session_state.play=r["id"]

# BROWSE
if page=="Browse":
    for item in catalog:
        st.markdown("### "+item["title"])
        st.write(item["description"])
        c1,c2=st.columns(2)
        with c1:
            if st.button("▶ Play "+item["id"]):
                st.session_state.play=item["id"]
        with c2:
            st.link_button("⬇ Download",
            f"https://drive.google.com/uc?export=download&id={item['fileId']}")

# PLAYER
if page=="Now Playing":
    pid=st.session_state.play
    if pid:
        item=[x for x in catalog if x["id"]==pid][0]
        st.subheader(item["title"])

        c1,c2,c3=st.columns(3)
        with c1:
            st.button("⏮ Previous")
        with c2:
            st.button("⏸ Pause")
        with c3:
            st.button("⏭ Next")

        st.components.v1.iframe(drive_preview(item["fileId"]),height=520)

# TRANSCRIPTS
if page=="Transcripts":
    for i in catalog:
        st.markdown("### "+i["title"])
        st.write(i.get("transcript","No transcript"))

# ANALYTICS
if page=="Analytics":
    st.write("Analytics dashboard coming soon")

# TEAM
if page=="R&D Team":
    st.subheader(team.get("team_name","Team"))
    if team.get("mission"): st.write(team["mission"])
    for m in team.get("members",[]):
        st.markdown("**"+m["name"]+"**")
        st.caption(m.get("role",""))

# ABOUT
if page=="About":
    st.write("Project ALBACAT — Islamic lecture streaming library.")
