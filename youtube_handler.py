import os, pickle, asyncio, logging, glob
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class YouTubeManager:
    SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

    def __init__(self, base_dir):
        self.base_dir = base_dir
        json_candidates = glob.glob(os.path.join(self.base_dir, "client_secret*.json"))
        self.secret_file = json_candidates[0] if json_candidates else None
        self.token_file = os.path.join(self.base_dir, 'token.pickle')
        self.youtube = None

    def authenticate(self):
        credentials = None
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                credentials = pickle.load(token)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                try: credentials.refresh(Request())
                except: credentials = None
            if not credentials:
                if not self.secret_file: raise FileNotFoundError("client_secret.jsonが見つかりません。")
                flow = InstalledAppFlow.from_client_secrets_file(self.secret_file, self.SCOPES)
                credentials = flow.run_local_server(port=0)
            with open(self.token_file, 'wb') as token: pickle.dump(credentials, token)
        self.youtube = build('youtube', 'v3', credentials=credentials, static_discovery=False)

    async def add_video_to_playlist(self, video_id, playlist_id):
        """戻り値: (成功したか, クォータ制限か)"""
        if not self.youtube: return False, False
        try:
            request = self.youtube.playlistItems().insert(
                part="snippet",
                body={"snippet": {"playlistId": playlist_id, "resourceId": {"kind": "youtube#video", "videoId": video_id}}}
            )
            await asyncio.get_event_loop().run_in_executor(None, request.execute)
            return True, False
        except HttpError as e:
            if e.resp.status in [403]: # クォータ超過
                logging.warning(f"YouTube API クォータ制限に達しました: {video_id}")
                return False, True
            logging.error(f"YouTube APIエラー: {e}")
            return False, False
        except Exception as e:
            logging.error(f"予期せぬエラー: {e}")
            return False, False