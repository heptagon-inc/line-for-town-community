import os
import sys

import csv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import dynamodb

def handler(event, context):
    """
    ゴミの収集日テーブルに対して、csvから一括でインポートします

    csvの形式は以下の通りです
    id,prefix,weekday,category

      id -> 連番を振ってください
      prefix -> 第2月曜日の「2」にあたる部分です（毎週の場合は0を指定してください）
      weekday -> 第2月曜日の「月」にあたる部分です
      category -> 何の収集日かを入れてください（「燃やせるゴミ」「缶」「ペットボトル」など）
    """

    with open('files/schedules.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            dynamodb.insert_schedule_data(int(row[0]), int(row[1]), row[2], row[3])
