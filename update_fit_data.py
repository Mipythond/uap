from model.db import DatabaseClient
from model.google_fit import GoogleFitClient

# 毎日定期実行される内容を記述する
def main():
    # db: INSTANCE GENERATION
    db_client = DatabaseClient()
    
    # db: group_idを指定して所属する全てのユーザ情報を取得
    users = db_client.get_users_by_group(1)
    
    # gf: 過去のfitデータをまとめて取得
    gf_data_list = []
    for user in users:
        gf_client = GoogleFitClient(user.user_id)
        gf_data = gf_client.fetch_past_data(5)
        for gfd in gf_data:
            gfd['steps'] *= user.steps_coefficient #steps補正
        print(gf_data)
        gf_data_list += gf_data #　一つのリストにまとめる
    
    # db: update
    for gf_data in gf_data_list:
        db_client.update_fit_data(gf_data)
    
if __name__ == "__main__":
    main()