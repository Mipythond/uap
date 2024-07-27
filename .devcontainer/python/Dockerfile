FROM python:latest

# パッケージリストを更新し、一般的な依存関係をインストール
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y build-essential

# pipとsetuptoolsの更新
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools

# requirements.txtをコンテナにコピー
COPY ./python/requirements.txt /workspace/requirements.txt

# 必要なパッケージをインストール
RUN pip install -r /workspace/requirements.txt

# ワークディレクトリを設定
WORKDIR /workspace
