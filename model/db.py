from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import extract  # extract関数をインポート
from datetime import datetime

# ベースクラスの作成
Base = declarative_base()

# グループテーブルのモデル
class Group(Base):
    __tablename__ = 'tbl_group'

    group_id = Column(Integer, primary_key=True, autoincrement=True)
    group_name = Column(String, nullable=False)

    # リレーションシップ
    users = relationship("User", back_populates="group")

# ユーザーテーブルのモデル
class User(Base):
    __tablename__ = 'tbl_user'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String, nullable=False)
    group_id = Column(Integer, ForeignKey('tbl_group.group_id'))

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

    def add_fit_data(self, user_id, steps, distance, weight, fat):
        try:
            new_fit_data = FitData(
                user_id=user_id,
                datetime=datetime.now(),
                steps=steps,
                distance=distance,
                weight=weight,
                fat=fat
            )
            self.session.add(new_fit_data)
            self.session.commit()
        except:
            self.session.rollback()
            raise
        finally:
            self.session.close()
    
    def get_user_fit_data_for_current_month(self, user_id):
        """指定されたuser_idの今月のfit_dataを取得"""
        try:
            # 現在の年と月
            now = datetime.now()
            current_year = now.year
            current_month = now.month

            # 指定したユーザーの今月のデータを取得
            fit_data = self.session.query(FitData).filter(
                FitData.user_id == user_id,
                extract('year', FitData.datetime) == current_year,
                extract('month', FitData.datetime) == current_month
            ).all()
            return fit_data
        finally:
            self.session.close()
            
# 使用例
if __name__ == "__main__":
    db_client = DatabaseClient()
    user_fit_data_this_month = db_client.get_user_fit_data_for_current_month(5)
    for data in user_fit_data_this_month:
        print(f"Date: {data.datetime}, Steps: {data.steps}, Distance: {data.distance}, Weight: {data.weight}, Fat: {data.fat}")

