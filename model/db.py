from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import extract  # extract関数をインポート
from datetime import datetime
import json

# ベースクラスの作成
Base = declarative_base()

# グループテーブルのモデル
class Group(Base):
    __tablename__ = 'tbl_group'

    group_id = Column(Integer, primary_key=True, autoincrement=True)
    group_name = Column(String, nullable=False)
    discord_guild_id = Column(Integer, nullable=False)

    # リレーションシップ
    users = relationship("User", back_populates="group")

# ユーザーテーブルのモデル
class User(Base):
    __tablename__ = 'tbl_user'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String, nullable=False)
    group_id = Column(Integer, ForeignKey('tbl_group.group_id'))
    discord_user_id = Column(Integer, nullable=False)
    discord_roles = Column(JSON)

    # リレーションシップ
    group = relationship("Group", back_populates="users")
    fit_data = relationship("FitData", back_populates="user")

# 健康データテーブルのモデル
class FitData(Base):
    __tablename__ = 'tbl_fit'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('tbl_user.user_id'), nullable=False)
    datetime = Column(DateTime, nullable=False)
    steps = Column(Integer)
    distance = Column(Float)
    weight = Column(Float)
    fat = Column(Float)

    # リレーションシップ
    user = relationship("User", back_populates="fit_data")

# AWS RDSの接続情報
DATABASE_TYPE = ''
DB_HOST = ''
DB_NAME = ''
DB_USER = ''
DB_PASSWORD = ''
DB_PORT = ''

# 接続URLを生成
DATABASE_URL = f'{DATABASE_TYPE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# データベースとの接続設定
engine = create_engine(DATABASE_URL)

# セッションの作成
Session = sessionmaker(bind=engine)

class DatabaseClient:
    def __init__(self):
        self.session = Session()

    def get_all_users(self):
        try:
            users = self.session.query(User).all()
            return users
        finally:
            self.session.close()

    def get_user_fit_data(self, user_id):
        try:
            return self.session.query(FitData).filter_by(user_id=user_id).all()
        finally:
            self.session.close()

    def add_user(self, user_name, group_id=None):
        try:
            new_user = User(user_name=user_name, group_id=group_id)
            self.session.add(new_user)
            self.session.commit()
        except:
            self.session.rollback()
            raise
        finally:
            self.session.close()

    def get_users_by_group(self, group_id):
        try:
            users = self.session.query(User).filter_by(group_id=group_id).all()
            return users
        finally:
            self.session.close()
    
    def get_discord_guild_id(self, group_id):
        try:
            group = self.session.query(Group).filter_by(group_id=group_id).first()
            return group.discord_guild_id
        finally:
            self.session.close()

    def add_fit_data(self, fit_data, datetime=datetime.now()):
        try:
            new_fit_data = FitData(
                user_id=fit_data['user_id'],
                datetime=datetime,
                steps=fit_data['steps'],
                distance=fit_data['distance'],
                weight=fit_data['weight'],
                fat=fit_data['body_fat_percentage']
            )
            self.session.add(new_fit_data)
            self.session.commit()
        except:
            self.session.rollback()
            raise
        finally:
            self.session.close()
    
    # 最新データを取得するメソッド
    def get_latest_user_fit_data(self, user_id):
        """指定されたuser_idの最新のfit_dataを取得"""
        try:
            # クエリの最適化
            fit_data = self.session.query(FitData).filter(
                FitData.user_id == user_id
            ).order_by(FitData.datetime.desc()).limit(1).first()
            return fit_data
        finally:
            self.session.close()
    
    def get_user_fit_data_for_current_month(self, user_id):
        """指定されたuser_idの今月のfit_dataを取得"""
        try:
            # 現在の年と月
            now = datetime.now()
            current_year = now.year
            current_month = now.month
            
            # 月初だけは先月のデータを表示
            if now.day == 1:
                if current_month == 1:
                    current_month = 12
                else:
                    current_month-= 1

            # 指定したユーザーの今月のデータを取得
            fit_data = self.session.query(FitData).filter(
                FitData.user_id == user_id,
                extract('year', FitData.datetime) == current_year,
                extract('month', FitData.datetime) == current_month
            ).all()
            return fit_data
        finally:
            self.session.close()
    
    def update_fit_data(self, fit_data):
        """データベースに該当日のデータがあれば更新"""
        try:
            # 該当のデータが存在するかを確認
            existing_data = self.session.query(FitData).filter(
                FitData.user_id == fit_data['user_id'],
                extract('year', FitData.datetime) == fit_data['datetime'].year,
                extract('month', FitData.datetime) == fit_data['datetime'].month,
                extract('day', FitData.datetime) == fit_data['datetime'].day
            ).first()
            # データが既存の場合のみ更新する
            if existing_data:
                existing_data.steps = fit_data['steps']
                existing_data.distance = fit_data['distance']
                
            # データベースに反映
            self.session.commit()
        except:
            self.session.rollback()
            raise
        finally:
            self.session.close()
    
    # ユーザーのdiscord_rolesを更新するメソッド
    def update_discord_roles(self, user_id, roles):
        try:
            # ユーザーを取得
            user = self.session.query(User).filter_by(user_id=user_id).first()
            if user:
                # rolesリストをJSON形式に変換してdiscord_rolesカラムに設定
                user.discord_roles = json.dumps(roles)
                self.session.commit()
                print(f"User ID {user_id} のdiscord_rolesを更新しました。")
            else:
                print(f"User ID {user_id} が見つかりません。")
        except Exception as e:
            self.session.rollback()
            print(f"エラーが発生しました: {e}")
        finally:
            self.session.close()
