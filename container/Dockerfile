# Python Verison: 3.11
FROM python:3.11-slim-bookworm

ENV OMP_NUM_THREADS=16

RUN apt-get update && \
    apt-get install -y zip libatlas3-base libssl-dev libcerf-dev \
    liblapack-dev \
    libgomp1 \
    libgsl-dev \
    libcerf-dev \
    libreoffice \
    poppler-utils \
 && rm -rf /var/lib/apt/lists/*
RUN ln -s /usr/lib/x86_64-linux-gnu/libgsl.so /usr/lib/x86_64-linux-gnu/libgsl.so.25

COPY pip.conf /etc/pip.conf

# appディレクトリを作成
WORKDIR /app

# 必要なPythonライブラリのインストール
COPY requirements.txt /app
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# プログラムや設定ファイルなどをコピーする
COPY main.py /app
COPY modules/ /app/modules/
COPY packages/ /app/packages/
RUN chmod u+x packages/pseudo_voigt/activeshirley_gcc.exe
