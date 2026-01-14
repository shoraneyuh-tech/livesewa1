import sys import subprocess
import threading import os import time import streamlit as st from google.oauth2.service_account import Credentials from googleapiclient.discovery import build import requests

================= CONFIG =================

SERVICE_ACCOUNT_FILE = 'service_account.json' SCOPES = ['https://www.googleapis.com/auth/drive.readonly'] DRIVE_FOLDER_ID = 'ISI_FOLDER_ID_KAMU' STREAM_KEY = os.getenv('YT_STREAM_KEY')  # set di Streamlit Cloud Secrets

================= GOOGLE DRIVE =================

@st.cache_resource def get_drive_service(): creds = Credentials.from_service_account_file( SERVICE_ACCOUNT_FILE, scopes=SCOPES ) return build('drive', 'v3', credentials=creds)

def list_drive_videos(): service = get_drive_service() query = f"'{DRIVE_FOLDER_ID}' in parents and mimeType contains 'video/' and trashed=false" res = service.files().list( q=query, fields='files(id,name)', orderBy='name' ).execute() return res.get('files', [])

def download_video(file_id, filename): creds = Credentials.from_service_account_file( SERVICE_ACCOUNT_FILE, scopes=SCOPES ) creds.refresh(requests.Request()) headers = {"Authorization": f"Bearer {creds.token}"} url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"

with requests.get(url, headers=headers, stream=True) as r:
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(1024 * 1024):
            if chunk:
                f.write(chunk)

================= FFMPEG =================

def stream_video(video_path): rtmp = f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}" cmd = [ 'ffmpeg', '-re', '-i', video_path, '-c:v', 'libx264', '-preset', 'veryfast', '-b:v', '2500k', '-maxrate', '2500k', '-bufsize', '5000k', '-g', '60', '-keyint_min', '60', '-c:a', 'aac', '-b:a', '128k', '-f', 'flv', rtmp ] subprocess.run(cmd)

================= AUTO LOOP =================

def auto_stream(): videos = list_drive_videos() for v in videos: temp = 'current.mp4' st.write(f"▶ Streaming: {v['name']}") download_video(v['id'], temp) stream_video(temp) if os.path.exists(temp): os.remove(temp) time.sleep(2)

================= UI =================

st.set_page_config(page_title='FULL AUTO YT LIVE', layout='wide') st.title('🔴 FULL OTOMATIS YouTube Live') st.write('Tanpa klik. Playlist otomatis dari Google Drive.')

if not STREAM_KEY: st.error('STREAM KEY belum di-set di Secrets!') else: st.success('Streaming berjalan otomatis...') auto_stream()
