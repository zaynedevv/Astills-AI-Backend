import io
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload
from io import BytesIO


from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle, os

SCOPES = ["https://www.googleapis.com/auth/drive"]

# OAuth login
def get_drive_service():
    creds = None
    if os.path.exists("token.json"):
        with open("token.json", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "wb") as token:
            pickle.dump(creds, token)
    return build("drive", "v3", credentials=creds)

service = get_drive_service()
def upload_file(buffer: BytesIO, drive_name: str):
    """
    Upload a file to personal Google Drive directly from a BytesIO buffer.
    Keeps the specified parent folder ID.
    """
    buffer.seek(0)
  

    file_metadata = {
        "name": drive_name,
        "parents": ["1tsiBv5OAPnfF0o36vxcGz1AnNPdAMtcg"],
        "mimeType": "application/vnd.google-apps.document"  # convert DOCX → Google Docs
    }

    media = MediaIoBaseUpload(buffer, mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    uploaded = service.files().create(body=file_metadata, media_body=media, fields="id").execute()


    print(f"Uploaded file ID: {uploaded['id']}")
    return uploaded["id"]


def export_as_pdf(file_id, out_path):
    """Export a Drive file as PDF."""
    request = service.files().export(fileId=file_id, mimeType="application/pdf")
    with open(out_path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"Downloading {int(status.progress() * 100)}%")
    print(f"Saved PDF: {out_path}")


def delete_file(file_id):
    """Delete a file from personal Drive."""
    service.files().delete(fileId=file_id).execute()
    print(f"Deleted file: {file_id}")
