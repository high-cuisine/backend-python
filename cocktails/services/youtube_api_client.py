import os

from google.auth.transport import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload


class YouTubeApiClient:
    def __init__(self, client_secret_file="client_secret.json", token_file="user_token.json"):
        self.SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
        self.client_secret_file = client_secret_file
        self.token_file = token_file
        self.youtube = None

    def _authenticate(self):
        creds = None

        # Пробуем загрузить сохраненные credentials
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)

        # Если credentials недействительны или отсутствуют
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secret_file, self.SCOPES)
                creds = flow.run_local_server(port=2000)

            # Сохраняем credentials для будущих использований
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())

        return creds

    def _get_youtube_service(self):
        if not self.youtube:
            creds = self._authenticate()
            self.youtube = build('youtube', 'v3', credentials=creds)
        return self.youtube

    def upload_video(
            self,
            video_stream,
            title="",
            description="",
            privacy_status="private",
            tags=None,
            content_type='video/mp4'
    ):

        try:
            youtube = self._get_youtube_service()

            if tags is None:
                tags = []

            body = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "categoryId": '26'
                },
                "status": {
                    "privacyStatus": privacy_status
                }
            }

            media = MediaIoBaseUpload(video_stream, mimetype=content_type, chunksize=-1, resumable=True)

            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )

            response = request.execute()
            video_id = response['id']
            print(f"Видео успешно загружено! ID: {video_id}")
            print(f"Ссылка: https://youtu.be/{video_id}")
            return f'https://www.youtube.com/watch?v={video_id}'

        except HttpError as e:
            print(f"Ошибка YouTube API: {e}")
            return None
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            return None
