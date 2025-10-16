# RDEデータセットテンプレート　RDE_PEAK_SEPARATION　を試してみる

RDEデータセットテンプレート `RDE_PEAK_SEPARATION`　をローカル開発環境で動かす方法を説明します。

このRDEデータセットテンプレートは、ビルド済みのプログラムをを利用するためDockerコンテナを利用して実行する必要があります。そのため、この文書ではDockerコンテナのビルド方法、コンテナを実行して解析結果を取得する方法を説明します。

なお、入力する測定データ(RAWデータ)は提供していませんので各自でご用意ください。

## 準備
以下の開発環境を用意してください。
- Docker (Community Edition)
  - ベアメタル(非Docker)環境では動かすことはできません
  - ピーク分離のプログラムは実行形式で提供しており、それを組み込んでDockerコンテナを作成します

ファイル一式の入手
- git cloneまたはdownload zipでファイル一式を取得
- zipファイルで取得した場合は適宜フォルダに解凍する
- この説明では入手したファイルの解凍先を `work` フォルダと呼ぶことにします

## ファイルなどの説明
workフォルダには以下の内容のフォルダが用意されています
- container
  - 構造化処理プログラム一式が含まれています
  - 利用するpythonのパッケージはrequirements.txtを参照
- docs
  - 説明書など 
- template
  - 構造化処理プログラム以外のデータセットテンプレートを構成するファイルが含まれています
  - テンプレートによって含まれるファイルの構成が異なります

## 動かしてみる、それと解説

動かしてみるまでの手順は以下の通り
1. [Docker環境作成](#docker環境作成)
2. [コンテナ作成 実行](#コンテナ作成_実行)
3. [ファイルの配置](#ファイルの配置)
4. [プログラムの実行](#プログラムの実行)

### Docker環境作成

- Dockerクライアントを利用します。
- 既にDockerクライアントがインストール済みの場合は、下記1.～8.の手順は実行せずに、[コンテナ作成 実行](#コンテナ作成_実行)に進んで下さい。
- 導入手順は標準的な方法を記しています。導入先環境によっては手順通りに進められない場合がありますが、その点はご了承ください。


ターミナルを使ったコマンドラインでの操作で説明します(Ubuntu24.04上)
1. 必要な依存パッケージをインストールします。
    ```cmd
    sudo apt update
    sudo apt install apt-transport-https ca-certificates curl software-properties-common
    ```
2. Dockerの公式GPGキーを追加します。
    ```cmd
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    ```
3. Dockerのリポジトリを追加します。
    ```cmd
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    ```
4. リポジトリ情報を更新して、Dockerをインストールします。
    ```cmd
    sudo apt update
    sudo apt install docker-ce
    ```
5. インストールが完了したら、Dockerを起動します。
    ```cmd
    sudo service docker start
    ```
6. (非rootユーザーで使うため) 自分のユーザーを`docker`グループに追加します。
    ```cmd
    sudo usermod -aG docker $USER
    ```
7. 変更を反映させるために、WSLを再起動します。
    ```cmd
    exit
    ```
8. 再度、WSLにログインして、`docker`コマンドを`sudo`なしで使えるか確認します。
    ```cmd
    docker --version
    ```

### コンテナ作成
1. workフォルダに移動
2. Dockerコンテナを作成 (build)
    ```cmd
    $ docker build --no-cache --pull --rm -f "container/Dockerfile" -t nims_mdpf_shared_peak_separation:v1.0.0 "container"
    ```
3. Dockerコンテナを走らせる (run)
    ```cmd
    $ docker run --rm nims_mdpf_shared_peak_separation:v1.0.0 python main.py
    ```
4. 上記の実行結果は取り込みファイルなどを用意していないためpythonのエラーが表示されます。pythonのエラーが表示されればこの時点での動作確認は完了です。

### ファイルの配置

- Dockerコンテナの実行時にローカルフォルダをマウントする方法としています
- このため、入力ファイルをコンテナにコピーしたり、出力ファイルをローカルフォルダにコピーするという手間が省けます
- また、マウントするフォルダを複数用意しておけば、実行の際にマウント先を切り替えるだけで処理が行えます

containerフォルダに移動し、以下の通りファイルを配置してください。

1. フォルダの作成 (構造化処理用補助ファイル用、送状用、入力ファイル用)
    ```cmd
    $ cd container
    $ mkdir -p data/invoice
    $ mkdir data/inputdata
    ```
2. 入力データの配置
    - 入力データをdata/inputdata以下に配置します(dataの部分は別の名称でも良い)
    - 入力データは各自ご用意してください
    - この説明ではsample.csvというファイルを使っています
3. 送状ファイルの配置
    - 送状ファイル(invoice.json)をdata/invoice以下に配置します
    - invoice.jsonのサンプルは、tryout/invoice_sample.jsonにありますので、名前をinvoice.jsonに変えて利用してください
 4. 以下のようなファイルの配置とします
    ```cmd
    $ tree data
    data
    ├── inputdata
    │   └── sample.csv
    └── invoice
        └── invoice.json
    ```


### プログラムの実行
1. 用意したdataフォルダをコンテナにボリュームマウントして実行します<br>結果はdataフォルダ以下に出力されます
    - $(PWD)は、コマンドを実行しているワークディレクトリを取得するための記述です
    - コンテナ上で処理が実行されますが、入力ファイルはdataフォルダから読み、出力ファイルはdataフォルダに書き出されます
    ```cmd
    $ docker run --rm -v $(pwd)/data:/app/data nims_mdpf_shared_peak_separation:v1.0.0 python main.py
    ```
2. 確認
    - 正常終了すると以下のようにファイルが出力されます (以下例)
    ```cmd
    $ tree data
    data
    ├── attachment
    ├── inputdata
    │   └── sample.csv
    ├── invoice
    │   └── invoice.json
    ├── invoice_patch
    ├── logs
    │   ├── process.log
    │   └── rdesys.log
    ├── main_image
    │   └── sample_summary0001-1.png
    ├── meta
    │   └── metadata.json
    ├── nonshared_raw
    │   └── sample.csv
    ├── other_image
    │   ├── BIC_vs_NumPeak.png
    │   ├── gbp_rank10_numPeak1_auto_shirley_result.png
    ...略
    │   ├── input_spectrum2.png
    │   └── sample_summary0001-2.png
    ├── raw
    ├── structured
    │   ├── gbp_rank10_numPeak1_auto_shirley_parameters.csv
    │   ├── gbp_rank10_numPeak1_auto_shirley_result.csv
    ...略
    │   ├── gbp_rank9_numPeak2_auto_shirley_parameters.csv
    │   ├── gbp_rank9_numPeak2_auto_shirley_result.csv
    │   ├── result_figures.pptx
    │   └── summary_BIC.csv
    ├── tasksupport
    │   ├── default_value.csv
    │   ├── invoice.schema.json
    │   ├── metadata-def.json
    │   └── rdeconfig.yaml
    ├── temp
    │   ├── image
    │   ├── invoice_org.json
    │   ├── sample.csv
    │   └── sample_summary.pdf
    └── thumbnail
        └── sample_summary0001-1.png

    16 directories, 50 files

    ```


