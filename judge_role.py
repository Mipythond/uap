import streamlit as st
import pandas as pd
import json
from model.db import DatabaseClient

# discordのrole_idをJSONから取得
with open('config/roles.json', 'r') as f:
    discord_roles = json.load(f)

# db: INSTANCE GENERATION
db_client = DatabaseClient()

# db: group_idを指定して所属する全てのユーザのuser_idを取得
user_ids = []
users = db_client.get_users_by_group(1)
for user in users:
    user_ids.append(user.user_id)

# user_idをキーにした辞書に変換
user_dict = {user.user_id: user.user_name for user in users}

# db: userごとの今月のfit dataを取得
fit_data_monthly_list = []  # 2重配列
for user_id in user_ids:
    fit_data_monthly = db_client.get_user_fit_data_for_current_month(user_id)
    fit_data_monthly_list.append(fit_data_monthly)

# データをフラットにしてDataFrameに変換
fit_data_flat = []
for sublist in fit_data_monthly_list:
    for item in sublist:
        fit_data_flat.append({
            'user_id': item.user_id,
            'datetime': item.datetime,
            'steps': item.steps,
            'distance': item.distance,
            'weight': item.weight,
            'fat': item.fat
        })

# DataFrameに変換
df = pd.DataFrame(fit_data_flat)
# datetime列をdatetime型に変換
df['datetime'] = pd.to_datetime(df['datetime'])
# 各ユーザーごとに歩数と距離を累積計算
df['cumulative_steps'] = df.groupby('user_id')['steps'].cumsum()
df['cumulative_distance'] = df.groupby('user_id')['distance'].cumsum()

print(df.head(15))

# user_idごとにstepsの最大値、最小値、10000を超えている件数、cumulative_distanceの最大値を評価
steps_stats_per_user = df.groupby('user_id').agg(
    max_steps=('steps', 'max'),
    min_steps=('steps', 'min'),
    count_over_10000=('steps', lambda x: (x > 10000).sum()),
    cumulative_distance=('cumulative_distance', 'last')
).reset_index()

# 特定の条件を満たす場合に処理を行う
for _, row in steps_stats_per_user.iterrows():
    roles = []
    # 最大歩数ロール判定
    if row['max_steps'] >= 50000:
        roles.append(discord_roles['ROLE_ID_MAX_STEP_50000'])
    elif row['max_steps'] >= 40000:
        roles.append(discord_roles['ROLE_ID_MAX_STEP_40000'])
    elif row['max_steps'] >= 30000:
        roles.append(discord_roles['ROLE_ID_MAX_STEP_30000'])
    elif row['max_steps'] >= 20000:
        roles.append(discord_roles['ROLE_ID_MAX_STEP_20000'])
    else:
        pass # 何もしない
        
    # 最小歩数ロール判定
    if row['min_steps'] < 1000:
        roles.append(discord_roles['ROLE_ID_MIN_STEP_1000_UNDER'])
    elif row['min_steps'] <= 5000:
        roles.append(discord_roles['ROLE_ID_MIN_STEP_5000'])
    elif row['min_steps'] <= 1000:
        roles.append(discord_roles['ROLE_ID_MIN_STEP_10000'])
    else:
        pass # 何もしない
    
    # 10000歩超え回数ロール判定
    if row['count_over_10000'] >= 13:
        roles.append(discord_roles['ROLE_ID_10000_STEP_COUNT_13_OVER'])
    elif row['count_over_10000'] == 12:
        roles.append(discord_roles['ROLE_ID_10000_STEP_COUNT_12'])
    elif row['count_over_10000'] == 11:
        roles.append(discord_roles['ROLE_ID_10000_STEP_COUNT_11'])
    elif row['count_over_10000'] == 10:
        roles.append(discord_roles['ROLE_ID_10000_STEP_COUNT_10'])
    elif row['count_over_10000'] == 9:
        roles.append(discord_roles['ROLE_ID_10000_STEP_COUNT_9'])
    elif row['count_over_10000'] == 8:
        roles.append(discord_roles['ROLE_ID_10000_STEP_COUNT_8'])
    elif row['count_over_10000'] == 7:
        roles.append(discord_roles['ROLE_ID_10000_STEP_COUNT_7'])
    elif row['count_over_10000'] == 6:
        roles.append(discord_roles['ROLE_ID_10000_STEP_COUNT_6'])
    elif row['count_over_10000'] == 5:
        roles.append(discord_roles['ROLE_ID_10000_STEP_COUNT_5'])
    elif row['count_over_10000'] == 4:
        roles.append(discord_roles['ROLE_ID_10000_STEP_COUNT_4'])
    elif row['count_over_10000'] == 3:
        roles.append(discord_roles['ROLE_ID_10000_STEP_COUNT_3'])
    elif row['count_over_10000'] == 2:
        roles.append(discord_roles['ROLE_ID_10000_STEP_COUNT_2'])
    elif row['count_over_10000'] == 1:
        roles.append(discord_roles['ROLE_ID_10000_STEP_COUNT_1'])
    else:
        pass # 何もしない
    
    # 累積距離ロール判定
    if row['cumulative_distance'] >= 404:
        roles.append(discord_roles['ROLE_ID_CUMULATIVE_DISTANCE_404'])
    elif row['cumulative_distance'] >= 226:
        roles.append(discord_roles['ROLE_ID_CUMULATIVE_DISTANCE_226'])
    elif row['cumulative_distance'] >= 200:
        roles.append(discord_roles['ROLE_ID_CUMULATIVE_DISTANCE_200'])
    elif row['cumulative_distance'] >= 160:
        roles.append(discord_roles['ROLE_ID_CUMULATIVE_DISTANCE_160'])
    elif row['cumulative_distance'] >= 100:
        roles.append(discord_roles['ROLE_ID_CUMULATIVE_DISTANCE_100'])
    elif row['cumulative_distance'] >= 82:
        roles.append(discord_roles['ROLE_ID_CUMULATIVE_DISTANCE_84'])
    elif row['cumulative_distance'] >= 42:
        roles.append(discord_roles['ROLE_ID_CUMULATIVE_DISTANCE_42'])
    elif row['cumulative_distance'] >= 21:
        roles.append(discord_roles['ROLE_ID_CUMULATIVE_DISTANCE_21'])
    else:
        pass # 何もしない

    print(int(row['user_id']))
    print(roles)
    
    # db: ロールを更新
    db_client.update_discord_roles(int(row['user_id']), roles)
        
# 結果を表示
# print(steps_stats_per_user)