import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from model.db import DatabaseClient

# JSONファイルを読み込む
with open('config/user_color.json', 'r') as f:
    user_colors = json.load(f)

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

# PlotlyのFigureを各データのグラフ用に作成
fig_distance = go.Figure()
fig_weight = go.Figure()
fig_steps = go.Figure()
fig_cumulative_distance = go.Figure()
fig_cumulative_steps = go.Figure()

# 各ユーザーごとに異なる線を追加
for user_id, user_data in df.groupby('user_id'):
    # user config
    user_name = user_dict.get(user_id, 'who?')
    color = user_colors.get(str(user_id), '#000000')
    
    # 体重のグラフ
    fig_weight.add_trace(go.Scatter(
        x=user_data['datetime'],
        y=user_data['weight'],
        mode='lines+markers',
        name=f'{user_name}',
        line=dict(color=color)
    ))

    # 歩数のグラフ
    fig_steps.add_trace(go.Scatter(
        x=user_data['datetime'],
        y=user_data['steps'],
        mode='lines+markers',
        name=f'{user_name}',
        line=dict(color=color)
    ))
    
    # 距離のグラフ
    fig_distance.add_trace(go.Scatter(
        x=user_data['datetime'],
        y=user_data['distance'],
        mode='lines+markers',
        name=f'{user_name}',
        line=dict(color=color)
    ))

    # 累積歩数のグラフ
    fig_cumulative_steps.add_trace(go.Scatter(
        x=user_data['datetime'],
        y=user_data['cumulative_steps'],
        mode='lines+markers',
        name=f'{user_name}',
        line=dict(color=color)
    ))
    
    # 累積距離のグラフ
    fig_cumulative_distance.add_trace(go.Scatter(
        x=user_data['datetime'],
        y=user_data['cumulative_distance'],
        mode='lines+markers',
        name=f'{user_name}',
        line=dict(color=color)
    ))

# 各グラフのタイトルとレイアウトを設定
fig_weight.update_layout(
    title='体重変動',
    xaxis_title='Datetime',
    yaxis_title='Weight [kg]',
    legend=dict(orientation="h", 
                yanchor="bottom", 
                y=1.1, 
                xanchor="center", 
                x=0.5)
    )

fig_cumulative_steps.update_layout(
    title='今月の累計歩数',
    xaxis_title='Datetime',
    yaxis_title='Cumulative Steps',
    legend=dict(orientation="h", 
                yanchor="bottom", 
                y=1.1, 
                xanchor="center", 
                x=0.5)
    )

fig_steps.update_layout(
    title='歩数',
    xaxis_title='Datetime',
    yaxis_title='Steps',
    legend=dict(orientation="h", 
                yanchor="bottom", 
                y=1.1, 
                xanchor="center", 
                x=0.5)
    )

fig_cumulative_distance.update_layout(
    title='今月の累計移動距離',
    xaxis_title='Datetime',
    yaxis_title='Cumulative Distance [km]',
    legend=dict(orientation="h", 
                yanchor="bottom", 
                y=1.1, 
                xanchor="center", 
                x=0.5)
    )

fig_distance.update_layout(
    title='移動距離',
    xaxis_title='Datetime',
    yaxis_title='Distance [km]',
    legend=dict(orientation="h", 
                yanchor="bottom", 
                y=1.1, 
                xanchor="center", 
                x=0.5)
    )

#streamlitページ
col1, col2= st.columns([1, 5])  # 中央の列を広くする
# アイコン
with col1:
    st.image('image/uap_icon.png')  # 画像の幅を設定

# タイトル
with col2:
    st.write("""
    # United Athlete Program
    """)
    
# グラフ描画
st.plotly_chart(fig_weight)
st.plotly_chart(fig_cumulative_steps)
st.plotly_chart(fig_steps)
st.plotly_chart(fig_cumulative_distance)
st.plotly_chart(fig_distance)
