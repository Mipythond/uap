from model.db import DatabaseClient
from model.google_fit import GoogleFitClient

# 毎日定期実行される内容を記述する
def main():
    # db: INSTANCE GENERATION
    db_client = DatabaseClient()
    
    # db: group_idを指定して所属する全てのユーザのuser_idを取得
    user_ids = []
    users = db_client.get_users_by_group(1)
    for user in users:
        user_ids.append(user.user_id)
    
    # gf: 過去のfitデータをまとめて取得
    gf_data_list = []
    for user_id in user_ids:
        gf_client = GoogleFitClient(user_id)
        gf_data = gf_client.fetch_past_data(7)
        gf_data_list += gf_data #　一つのリストにまとめる
    
    # db: update
    for gf_data in gf_data_list:
        db_client.update_fit_data(gf_data)
    
if __name__ == "__main__":
    main()