import os
from datetime import datetime, timezone, timedelta
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

    # UTCで日またいでから実行する。前日の期間を取得する
    def get_dates(self):
         # 現在のUTC時間を取得
        now_utc = datetime.now(timezone.utc)
        # utcの00:00を取得してjstに変換
        end_jst = datetime(now_utc.year, now_utc.month, now_utc.day, tzinfo=timezone.utc) - timedelta(hours=9)
        # JSTの0時から24時の範囲をUTCに変換（JSTの次の日の0時 = UTCの15:00）
        start_date = end_jst - timedelta(days=1)  # 前日の00:00(JST)
        end_date = end_jst # 前日の24:00(JST)
        return start_date, end_date
    
    def get_past_dates(self, days_ago):
        # 現在のUTC時間を取得
        now_utc = datetime.now(timezone.utc)
        # utcの00:00を取得してjstに変換
        now_jst = datetime(now_utc.year, now_utc.month, now_utc.day, tzinfo=timezone.utc) - timedelta(hours=9)
        # JSTの0時から24時の範囲をUTCに変換（JSTの次の日の0時 = UTCの15:00）
        start_date = now_jst - timedelta(days=days_ago)  # 指定日数前の日付の00:00(JST)
        end_date = start_date + timedelta(days=1) # 指定日数前の日付の24:00(JST)
        return start_date, end_date
    
    """
    期間を指定してfitデータを取得する
    """
    def fetch_data(self, data_source, start_date, end_date):
        dataset_id = f"{int(start_date.timestamp() * 1e9)}-{int(end_date.timestamp() * 1e9)}"
        dataset = self.service.users().dataSources().datasets().get(
            userId='me',
            dataSourceId=data_source,
            datasetId=dataset_id
        ).execute()
        return dataset.get('point', [])

    def fetch_combined_data(self, start_date=None, end_date=None):
        data_sources = {
            "steps": "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps",
            "distance": "derived:com.google.distance.delta:com.google.android.gms:merge_distance_delta",
            "weights": "derived:com.google.weight:com.google.android.gms:merge_weight",
            "body_fat": "derived:com.google.body.fat.percentage:com.google.android.gms:merge_body_fat_percentage"
        }

        results = {
            "user_id": self.user_id,
            "steps": 0,
            "distance": 0.0,
            "weight": 0.0,
            "body_fat_percentage": 0.0
        }
        
        # 期間の指定がない場合は今日のデータを取得
        if start_date == None or end_date == None:
            start_date, end_date = self.get_dates()
            
        for key, data_source in data_sources.items():
            points = self.fetch_data(data_source, start_date, end_date)

            if key == "steps":
                for point in points:
                    for value in point['value']:
                        results["steps"] += value.get('intVal', 0)

            elif key == "distance":
                for point in points:
                    for value in point['value']:
                        results["distance"] += round(((value.get('fpVal', 0.0))/1000), 3)
                        
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
    
    # 日単位で期間を指定し、過去データを取得する
    def fetch_past_data(self, days_ago_period):
        data_sources = {
            "steps": "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps",
            "distance": "derived:com.google.distance.delta:com.google.android.gms:merge_distance_delta",
            "weights": "derived:com.google.weight:com.google.android.gms:merge_weight",
            "body_fat": "derived:com.google.body.fat.percentage:com.google.android.gms:merge_body_fat_percentage"
        }
        
        results_list = []
        
        # 一日づつ過去データを取得する
        for days_ago in range(1, days_ago_period, 1):
            start_date, end_date = self.get_past_dates(days_ago)
            results = {
                "user_id": self.user_id,
                "steps": 0,
                "distance": 0.0,
                "weight": 0.0,
                "body_fat_percentage": 0.0,
                "datetime": start_date + timedelta(days=1)# db探索用 dayのみ参照 一日ずらす
            }
            
            for key, data_source in data_sources.items():
                points = self.fetch_data(data_source, start_date, end_date)

                if key == "steps":
                    for point in points:
                        for value in point['value']:
                            results["steps"] += value.get('intVal', 0)

                elif key == "distance":
                    for point in points:
                        for value in point['value']:
                            results["distance"] += round(((value.get('fpVal', 0.0))/1000), 3)
                            
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
            # リストに追加
            results_list.append(results)
        return results_list
                