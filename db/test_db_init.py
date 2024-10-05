from model.db import DatabaseClient
import random
import datetime

# local環境での開発、testのためにdbにfitdatを入れるためのスクリプト
def main():
    # db: INSTANCE GENERATION
    db_client = DatabaseClient()
    
    # db: group_idを指定して所属する全てのユーザのuser_idを取得
    user_ids = []
    users = db_client.get_users_by_group(1)
    for user in users:
        user_ids.append(user.user_id)
        
    # 今月の1日から今日までのfit_dataを入れる
    # 現在のUTC時間を取得
    now_utc = datetime.datetime.now(datetime.UTC)
    # 1日
    dt = datetime.datetime(now_utc.year, now_utc.month, 1, tzinfo=datetime.UTC)
    
    for day in range(1, now_utc.day):
        # gf: 各ユーザのfit_dataを取得してリスト化
        fit_data_list = []
        for user_id in user_ids:
            gf_data = mock_get_fit_data(user_id)
            fit_data_list.append(gf_data)
            
        # # db: weight,fatが未更新の場合は直近のデータを引き継ぎ
        # for fit_data in fit_data_list:
        #     if fit_data['weight'] == 0.0: # MEMO: fatだけ記録されることはないはず
        #         latest_fit_data = db_client.get_latest_user_fit_data(fit_data['user_id'])
        #         fit_data['weight'] = latest_fit_data.weight
        #         fit_data['body_fat_percentage'] = latest_fit_data.fat
        
        # db: fit_date_listをdbへ書き込む
        for fit_data in fit_data_list:
            db_client.add_fit_data(fit_data, datetime=dt)
            print(fit_data)
            print(dt)
        
        dt += datetime.timedelta(days=1)

def mock_get_fit_data(user_id):
    results = {
        "user_id": user_id,
        "steps": random.randint(1000, 30000),
        "distance": round(random.uniform(1, 20), 3),
        "weight": round(random.uniform(60, 65), 3),
        "body_fat_percentage": 0.0
    }
    return results

if __name__ == "__main__":
    main()