# ピーク分離テンプレート

## 概要
- DT0013: ピーク分離テンプレート

スペクトルデータに対してフォークト関数を基底関数としてピーク分離を行い、その結果をベイズ情報量規準(BIC)で評価して上位の分離結果を出力するテンプレートです。
- 論理モデルは、疑似フォークト(pseudo voigt)関数と畳み込みフォークト(convolution voigt)関数に対応しています。
- 入力ファイルは、以下のデータに対応しています。(以下、例)
    ```
    35.0,409.0
    34.75,401.0
    34.5,394.0
    :
    ```
    - スペクトルデータは2列のCSV形式であること。
    - 第1列はエネルギーで降順に並んでいること。
    - 第2列は強度で0以上の正の実数値であること。

## メタ情報
- [メタ情報](docs/requirement_analysis/要件定義.xlsx)

## 基本情報

### コンテナ情報
- 【コンテナ名】nims_mdpf_shared_peak_separation:v1.1.0

### テンプレート情報
- DT0013:
    - 【データセットテンプレートID】NIMS_DT0013_PEAK_SEPARATION_v1.1
    - 【データセットテンプレート名日本語】Voigt関数を基底関数とした自動ピーク分離
    - 【データセットテンプレート名英語】XPS peak separation voigt
    - 【データセットテンプレートの説明】Voigt関数を基底関数とした自動ピーク分離
    - 【バージョン】1.1
    - 【データセット種別】計算値・理論値型
    - 【データ構造化】あり (システム上「あり」を選択)
    - 【取り扱い事業】NIMS研究および共同研究プロジェクト (PROGRAM)
    - 【装置名】(なし。装置情報を紐づける場合はこのテンプレートを複製し、装置情報を設定すること。)

### データ登録方法
- 送り状画面をひらいて入力ファイルに関する情報を入力する
- 「登録ファイル」欄に登録したいファイルをドラッグアンドドロップする。
    - 複数のファイルを入力し一度に複数のデータを登録することが可能。
    - 複数のファイルを入力する場合は、「データ名」に「${filename}」と入力し「データ名」に入力ファイル名をマッピングさせることができる。
- 「登録開始」ボタンを押して（確認画面経由で）登録を開始する

## 構成

### レポジトリ構成

```
peak_separation
├── LICENSE
├── README.md
├── container
│   ├── data (入出力(下記参照))
│   ├── modules (ソースコード)
│   │   ├── datasets_process.py (構造化処理の大元)
│   │   ├── graph_handler.py (グラフ描画)
│   │   ├── inputfile_handler.py (入力ファイル読み込み(共通部))
│   │   ├── interfaces.py
│   │   ├── invoice_handler.py (送り状上書き)
│   │   ├── meta_handler.py (メタデータ解析(共通部))
│   ├── packages (ピーク分離実行可能ファイル)
│   ├── src (ピーク分離ソースコード)
│   ├── tests (テストコード)
│   ├── docker.sh (ローカル実行用シェル)
│   ├── Dockerfile
│   ├── Dockerfile_make (ピーク分離実行可能ファイルコンパイル用)
│   ├── Dockerfile_test (ローカル環境テスト用)
│   ├── main.py
│   ├── pip.conf
│   ├── pyproject.toml
│   ├── requirements-test.txt
│   ├── requirements.txt
│   └── tox.ini
├── docs (ドキュメント)
│   ├── manual (マニュアル)
│   └── requirement_analysis (要件定義)
├── inputdata (サンプルデータ)
└── template (テンプレート群)
     ├── batch.yaml
     ├── catalog.schema.json (カタログ項目定義)
     ├── invoice.schema.json (送り状項目定義)
     ├── jobs.template.yaml
     ├── metadata-def.json (メタデータ定義)
     └── tasksupport
         ├── default_value.csv
         ├── invoice.schema.json (送り状項目定義)
         ├── metadata-def.json (メタデータ定義)
         └── rdeconfig.yaml (設定ファイル)
```

### 動作環境ファイル入出力

```
│   ├── container/data
│   │   ├── attachment
│   │   ├── inputdata
│   │   │   └── 登録ファイル欄にドラッグアンドドロップした任意のファイル
│   │   ├── invoice
│   │   │   └── invoice.json (送り状ファイル)
│   │   ├── main_image
│   │   │   └── *_summary0001-*.png (まとめスライドの画像)
│   │   ├── meta
│   │   │   └── metadata.json (空ファイル)
│   │   ├── nonshared_raw
│   │   │   └── inputdataからコピーした入力ファイル
│   │   ├── other_image
│   │   │   ├── BIC_vs_NumPeak.png (BIC vs. ピーク本数の図)
│   │   │   ├── *_result.png (ピーク分離画像)
│   │   │   └── input_spectrum2.png (入力スペクトルの図)
│   │   ├── structured
│   │   │   ├── *_parameters.csv (ピークパラメータの数字データ)
│   │   │   ├── *_result.csv (ピーク分離結果を描画するための数値データ)
│   │   │   ├── summary_BIC.csv (ピーク本数とBICの数値データ)
│   │   │   ├── result_figures.pptx (まとめスライドのパワーポイント)
│   │   ├── tasksupport (テンプレート群)
│   │   │   ├── default_value.csv
│   │   │   ├── invoice.schema.json
│   │   │   ├── metadata-def.json
│   │   │   └── rdeconfig.yaml
│   │   └── thumbnail
│   │       └── (サムネイル用)プロット画像
```

## データ閲覧
- データ一覧画面を開く。
- ギャラリー表示タブでは１データがタイル状に並べられている。データ名をクリックして詳細を閲覧する。
- ツリー表示タブではタクソノミーにしたがってデータを階層表示する。データ名をクリックして詳細を閲覧する。

### 動作環境
- Python: 3.12
- RDEToolKit: 1.7.1

### リリースノート
- 初版：2025-10-07
