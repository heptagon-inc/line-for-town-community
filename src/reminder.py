import os
import sys
import json
from datetime import datetime, timezone, timedelta

from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import dynamodb

UTC = timezone.utc
JST = timezone(timedelta(hours=+9), 'JST')

def handler(event, context):
    dt_time = datetime.strptime(event['time'].strip(), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=UTC)
    dt_time_jst = datetime.fromtimestamp(dt_time.timestamp(), JST)
    
    ymd = dt_time_jst.strftime('%Y/%m/%d')
    md = dt_time_jst.strftime('%m/%d')
    hm = dt_time_jst.strftime('%H:%M')
    
    print(ymd)
    print(hm)
    
    # 午後の通知は翌日の情報を通知する仕様
    if dt_time_jst.strftime('%p') == 'PM':
        dt_time_jst = dt_time_jst + timedelta(days=1)
        ymd = dt_time_jst.strftime('%Y/%m/%d')
        md = dt_time_jst.strftime('%m/%d')
        
    # 年末年始(12/30〜1/2)は休み（自治体によって修正してお使いください）
    if md in ['12/30', '12/31', '01/01', '01/02']:
        print("年末年始のため休み")
        return
    
    # 第何x曜日かを取得する
    d = int(dt_time_jst.strftime('%d'))
    prefix = -(-d // 7)
    wd = dt_time_jst.weekday()

    wd_ja = ["月","火","水","木","金","土","日"]
    print(ymd, 'は', f'第{prefix}{wd_ja[wd]}曜日')
    
    # 該当の曜日に収集されるゴミの種類を取得する
    schedules = dynamodb.scan_schedule_data(prefix, wd_ja[wd])

    if len(schedules) == 0:
        print("収集日の該当なし")
        return

    categories = [f'{s["category"]}の日' for s in schedules]
    categories_text = '\n'.join(categories)
     
    # 午前は当日の通知、午後は翌日の通知
    if dt_time_jst.strftime('%p') == 'AM':
        target = '今日'
        column_name = 'gomi_today'
    else:
        target = '明日'
        column_name = 'gomi_day_before'
    
    # pushする本文を作成
    text = f'{target}({ymd})は...\n\n{categories_text}\n\nです！お忘れなく！'
    
    # 送信先一覧を取得
    target_users = dynamodb.scan_users_who_need_to_push(column_name, hm)

    if len(target_users) == 0:
        print("送信対象なし")
        return
    
    # 送信対象にテキストを送信
    line_bot_api = LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])

    for user in target_users:
        try:
            line_bot_api.push_message(user["id"], TextSendMessage(text=text))
        except LineBotApiError as e:
            print(e)
