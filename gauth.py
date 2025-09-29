import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
TOKEN_FILE = Path("token.json")
CLIENT_SECRET = Path("client_secret.json")

def get_credentials() -> Credentials:
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # 自动刷新
            from google.auth.transport.requests import Request
            creds.refresh(Request())
        else:
            # 首次授权
            if not CLIENT_SECRET.exists():
                raise FileNotFoundError("client_secret.json 不存在，请放在项目根目录。")
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
            creds = flow.run_local_server(port=0)  # 本地回调
        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    return creds
