from model.db import DatabaseClient
from model.google_fit import GoogleFitClient
from datetime import datetime, timedelta

# 毎日定期実行される内容を記述する
def main():
    # db: INSTANCE GENERATION
    db_client = DatabaseClient()
    
    # db: group_idを指定して所属する全てのユーザのuser_idを取得
    user_ids = []
    users = db_client.get_users_by_group(1)
    for user in users:
        user_ids.append(user.user_id)
        
    # gf: 各ユーザのfit_dataを取得してリスト化
    fit_data_list = []
    for user_id in user_ids:
        gf_client = GoogleFitClient(user_id)
        gf_data = gf_client.fetch_combined_data()
        fit_data_list.append(gf_data)
    
    # db: weight,fatが未更新の場合は直近のデータを引き継ぎ
    for fit_data in fit_data_list:
        if fit_data['weight'] == 0.0: # MEMO: fatだけ記録されることはないはず
            latest_fit_data = db_client.get_latest_user_fit_data(fit_data['user_id'])
            fit_data['weight'] = latest_fit_data.weight
            fit_data['body_fat_percentage'] = latest_fit_data.fat
    
    # db: fit_date_listをdbへ書き込む
    # fitdataを取得する時間が早すぎると正しい値が取得できないので、
    # 朝10時にこのコードを実行するが、前日のデータを取得するのでdbに書き込む値はずらす
    datetime_db = datetime.now() - timedelta(hours=2)
    for fit_data in fit_data_list:
        db_client.add_fit_data(fit_data, datetime_db)
    
if __name__ == "__main__":
    main()