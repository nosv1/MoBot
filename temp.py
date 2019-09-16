from oauth2client.file import Storage
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.service_account import ServiceAccountCredentials 
import io
import httplib2
from apiclient.http import MediaIoBaseDownload
from pygdrive3 import service

import SecretStuff

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('MoBot_secret.json'), scope)

drive_service = service.DriveService("./MoBot_secret.json")

file_id = '1Ut8QSZ48uB-H1wpE3-NxpPwBKLybkK-uo6Jb5LOSIxY'
request = drive_service.files().export_media(fileId=file_id,
                                             mimeType='text/html')
fh = io.BytesIO()
downloader = MediaIoBaseDownload(fh, request)
done = False
while done is False:
    status, done = downloader.next_chunk()
    print("Download %d%%." % int(status.progress() * 100))