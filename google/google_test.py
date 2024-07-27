import os
import json
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# 認証情報のファイルパス
SCOPES = [
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/fitness.location.read',
    'https://www.googleapis.com/auth/fitness.body.read'
]
CREDENTIALS_FILE = 'uap_credential.json'
TOKEN_FILE = 'token.json'

def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return creds

def fetch_data(service, data_source, start_date, end_date):
    dataset_id = f"{int(start_date.timestamp() * 1e9)}-{int(end_date.timestamp() * 1e9)}"
    dataset = service.users().dataSources().datasets().get(
        userId='me',
        dataSourceId=data_source,
        datasetId=dataset_id
    ).execute()
    return dataset.get('point', [])

def fetch_daily_steps(service, start_date, end_date):
    data_source = "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
    points = fetch_data(service, data_source, start_date, end_date)

    steps = 0
    for point in points:
        for value in point['value']:
            steps += value['intVal']
    return steps

def fetch_daily_distance(service, start_date, end_date):
    data_source = "derived:com.google.distance.delta:com.google.android.gms:merge_distance_delta"
    points = fetch_data(service, data_source, start_date, end_date)

    distance = 0.0
    for point in points:
        for value in point['value']:
            distance += value['fpVal']
    return distance

    distance = 0.0
    for point in dataset.get('point', []):
        for value in point['value']:
            distance += value['fpVal']
    return distance

def fetch_weight(service, start_date, end_date):
    data_source = "derived:com.google.weight:com.google.android.gms:merge_weight"
    points = fetch_data(service, data_source, start_date, end_date)
    
    weights = []
    for point in points:
        for value in point['value']:
            weights.append(value['fpVal'])
    return weights

def fetch_body_fat(service, start_date, end_date):
    data_source = "derived:com.google.body.fat.percentage:com.google.android.gms:merge_body_fat_percentage"
    points = fetch_data(service, data_source, start_date, end_date)
    
    body_fat_percentages = []
    for point in points:
        for value in point['value']:
            body_fat_percentages.append(value['fpVal'])
    return body_fat_percentages

def main():
    creds = get_credentials()
    service = build('fitness', 'v1', credentials=creds)

    today = datetime.datetime.now(datetime.UTC).date()
    start_date = datetime.datetime(today.year, today.month, today.day, tzinfo=datetime.UTC)
    end_date = start_date + datetime.timedelta(days=1)

    steps = fetch_daily_steps(service, start_date, end_date)
    distance = fetch_daily_distance(service, start_date, end_date)
    weights = fetch_weight(service, start_date, end_date)
    body_fat_percentages = fetch_body_fat(service, start_date, end_date)

    print(f"Steps: {steps}")
    print(f"Distance: {distance} meters")
    print(f"Weights: {weights}")
    print(f"Body Fat Percentages: {body_fat_percentages}")

if __name__ == '__main__':
    main()
