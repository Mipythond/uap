import os
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

class GoogleFitClient:
    SCOPES = [
        'https://www.googleapis.com/auth/fitness.activity.read',
        'https://www.googleapis.com/auth/fitness.location.read',
        'https://www.googleapis.com/auth/fitness.body.read'
    ]
    
    CREDENTIALS_FILE = 'credential/uap_credential.json'

    def __init__(self, user_id):
        self.user_id = user_id
        self.TOKEN_FILE = f'credential/user/{user_id}_token.json'  # ユーザーIDに基づいたトークンファイルのパス
        self.creds = self.get_credentials()
        self.service = self.build_service()
        self.start_date, self.end_date = self.get_dates()

    def get_credentials(self):
        creds = None
        if os.path.exists(self.TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(self.TOKEN_FILE, self.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.CREDENTIALS_FILE, self.SCOPES)
                creds = flow.run_local_server(port=8080)
            with open(self.TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        return creds

    def build_service(self):
        return build('fitness', 'v1', credentials=self.creds)

    def get_dates(self):
        today = datetime.datetime.now(datetime.UTC).date()
        start_date = datetime.datetime(today.year, today.month, today.day, tzinfo=datetime.UTC)
        end_date = start_date + datetime.timedelta(days=1)
        return start_date, end_date

    def fetch_combined_data(self):
        data_sources = {
            "steps": "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps",
            "distance": "derived:com.google.distance.delta:com.google.android.gms:merge_distance_delta",
            "weights": "derived:com.google.weight:com.google.android.gms:merge_weight",
            "body_fat": "derived:com.google.body.fat.percentage:com.google.android.gms:merge_body_fat_percentage"
        }

        results = {
            "user_id": self.user_id,
            "steps": 0,
            "distance": 0,
            "weight": 0.0,
            "body_fat_percentage": 0.0
        }

        for key, data_source in data_sources.items():
            points = self.fetch_data(data_source)

            if key == "steps":
                for point in points:
                    for value in point['value']:
                        results["steps"] += value.get('intVal', 0)

            elif key == "distance":
                for point in points:
                    for value in point['value']:
                        results["distance"] += int(value.get('fpVal', 0.0))
                        
            elif key == "weights":
                for point in points:
                    if point['value']:  # 'value' が空でないことを確認
                        # 最後の要素を取得して追加
                        results["weight"] += round(point['value'][-1].get('fpVal', 0.0), 1)

            elif key == "body_fat":
                for point in points:
                    if point['value']:  # 'value' が空でないことを確認
                        # 最後の要素を取得して追加
                        results["body_fat_percentage"] += point['value'][-1].get('fpVal', 0.0)

        return results

    def fetch_data(self, data_source):
        dataset_id = f"{int(self.start_date.timestamp() * 1e9)}-{int(self.end_date.timestamp() * 1e9)}"
        dataset = self.service.users().dataSources().datasets().get(
            userId='me',
            dataSourceId=data_source,
            datasetId=dataset_id
        ).execute()
        return dataset.get('point', [])
