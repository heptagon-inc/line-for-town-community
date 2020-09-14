# line-for-town-community

町内会向けLINE公式アカウント用のバックエンドを作成します

　

# 構築手順

本プロジェクトは、serverless frameworkを使用して、AWS上に環境を構築します。<br/>
AWSのアカウント作成や、serverless framework本体やプラグインのインストール方法は、公式ページをご確認ください。

　

## (1)チャネルアクセストークンの取得
LINE公式アカウントを作成し、Messaging APIを有効にして、チャネルアクセストークン（長期）を発行してください。

　

## (2)ファイルの差し替え
`files`の中に含まれている以下のファイルを必要に応じて修正してください。

### richmenu_tmp.png
リッチメニュー用の画像です。

配置やサイズを修正した場合は、`src/create_richmenu.py`も修正してください。


### schedule.csv
ゴミの収集日のデータです。

`id,prefix,weekday,category` の順で作成してください（先頭行に見出しは不要です）

| 列名     | 型     | 説明                                                         |
| -------- | ------ | ------------------------------------------------------------ |
| id       | 数値   | 重複がないように振ってください（連番を推奨）                 |
| prefix   | 数値   | 「第2月曜日」の「2」にあたる部分です。<br/>毎週の場合は「0」を指定してください。 |
| weekday  | 文字列 | 「第2月曜日」の「月」にあたる部分です。<br/>「月/火/水/木/金/土/日」のいずれか一文字を指定してください。 |
| category | 文字列 | 何の収集日かを入れてください<br/>（「燃やせるゴミ」「缶」「ペットボトル」など） |

　

## (3)deploy
serverless frameworkのコマンドを使用してデプロイしてください。

```
serverless deploy -v \
--stage prd \
--group <YOUR_GROUP_NAME> \ 
--token <YOUR_LINE_CHANNEL_ACCESS_TOKEN> \
--secret <YOUR_LINE_CHANNEL_SECRET>
```

ここで設定した`stage`と`group`は、生成されるリソース名の接頭辞に使用されます。

（例) 
stageが「prd」、groupが「aaa」の場合、接頭辞は`line4tc-aaa-prd-`になります。

　

## (4)ゴミの収集日のデータをimport
csvからのimport用に用意されたLambdaを実行して、DynamoDB上に生成されたschedulesテーブルにデータをimportしてください。

```
serverless invoke --function ImportScheduleData \
--stage prd \
--group <YOUR_GROUP_NAME>
```

　

## (5)リッチメニューの作成
リッチメニュー作成用に用意されたLambdaを実行して、リッチメニューの作成と有効化の設定を行ってください。

```
serverless invoke --function CreateRichMenu \
--stage prd \
--group <YOUR_GROUP_NAME>
```

　

## (6)webhookのURLを設定
デプロイされたwebhook用APIのURLをコピーして、LINE公式アカウントのMessaging APIのWebhook URLに設定・保存してください。
