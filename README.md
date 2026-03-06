# Project ALBACAT v2

Store-style History Audio Library for lectures by **Albani Zaria**.
Audio files are hosted on **Google Drive** and referenced by `fileId`.

## Features (v2)
- Browse catalog (search + filters + sorting)
- Series playlist view (lecture-by-lecture)
- Now Playing with Next/Previous
- Seekable audio player (best-effort byte download)
- Playback speed control for smaller files (auto fallback for larger files)
- Google Drive preview fallback (reliable)

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Configure audio
Edit `catalog.json` and add each session with its `fileId`.

**Drive sharing must be:**
Anyone with the link → Viewer

## Deploy
Push to GitHub and deploy using Streamlit Community Cloud.
