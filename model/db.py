from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

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

# 接続URLを生成
DATABASE_URL = f'{DATABASE_TYPE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
# データベースとの接続設定
engine = create_engine(DATABASE_URL)  # SQLiteを使用していますが、他のDBも指定可能

# セッションの作成
Session = sessionmaker(bind=engine)
session = Session()

# 特定のユーザーのデータを取得
user_data = session.query(FitData).filter_by(user_id=1).all()

for data in user_data:
    print(data.datetime, data.steps, data.distance, data.weight, data.fat)
