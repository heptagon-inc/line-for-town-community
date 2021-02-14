import os
import sys
import json
import urllib

import base64
import hashlib
import hmac

from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import dynamodb


def handler(event, context):
    """
    LINEからのwebhookを処理します
    """

    if not is_valid_signature(event['headers']['x-line-signature'], event['body']):
        print("signature is not valid")
        return response()

    print("signature is valid")

    print(json.dumps(event))
    body = json.loads(event['body'])

    # 送られてくるイベントの数だけ実行
    for e in body['events']:
        dispatch(e)

    return response()


def response():
    return {
        "statusCode": 200,
        "headers": {},
        "body": "",
        "isBase64Encoded": False
    }


# ================================
# LINE
# ================================

def is_valid_signature(header_signature, body):
    channel_secret = os.environ['LINE_CHANNEL_SECRET']

    hash = hmac.new(channel_secret.encode('utf-8'), body.encode('utf-8'), hashlib.sha256).digest()
    calc_signature = base64.b64encode(hash).decode('utf-8')

    return header_signature == calc_signature


def push_message(user_id, text):
    line_bot_api = LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
    
    try:
        line_bot_api.push_message(user_id, TextSendMessage(text=text))
    except LineBotApiError as e:
        print(e)


def reply_message(reply_token, text):
    line_bot_api = LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
    
    try:
        line_bot_api.reply_message(reply_token, messages=[TextSendMessage(text=text)])
    except LineBotApiError as e:
        print(e)


# ================================
# Dispatcher
# ================================

def dispatch(event):
    event_type = event['type']
    print(event_type)
    
    if event_type == 'message':
        dispatch_message(event)
    elif event_type == 'postback':
        dispatch_postback(event)
    elif event_type == 'follow':
        dispatch_follow(event)
    elif event_type == 'unfollow':
        dispatch_unfollow(event)
    else:
        pass


# ================================
# Dispatcher - message
# ================================

def dispatch_message(event):
    message_type = event['message']['type']
    print(message_type)
    
    if message_type == 'text':
        dispatch_text_message(event)
    else:
        pass


def dispatch_text_message(event):
    user_id = event['source']['userId']
    text = event['message']['text']
    reply_token = event['replyToken']
    
    # おうむ返し
    reply_message(reply_token, text)


# ================================
# Dispatcher - follow / unfollow
# ================================
    
def dispatch_follow(event):
    user_id = event['source']['userId']

    dynamodb.create_user_if_needed(user_id)
    dynamodb.enable_user(user_id)


def dispatch_unfollow(event):
    user_id = event['source']['userId']
    
    dynamodb.disable_user(user_id)


# ================================
# Dispatcher - postback
# ================================
    
def dispatch_postback(event):
    user_id = event['source']['userId']
    
    postback = event['postback']

    # PostbackActionにはQueryString形式でパラメータをつけて送っている
    # （create_richmenu.pyを参照）
    data = urllib.parse.parse_qs(postback['data'])
    
    action = data['action'][0]
    print('action =', action)
    
    if action == 'check':
        check_settings(user_id)
    elif action == 'set':
        target = data['target'][0]
        print('target =', target)
        
        set_notification_time(user_id, target, postback)
    elif action == 'remove':
        target = data['target'][0]
        print('target =', target)
        
        remove_notification_time(user_id, target)
    else:
        pass


def check_settings(user_id):
    """
    指定ユーザーの通知時間の設定を取得して、通知します

    Parameters
    ----------
    user_id : string
        ユーザーID
    """
    user = dynamodb.get_user(user_id)
    
    if user is not None:
        gomi_today = user.get('gomi_today', '(設定なし)')
        gomi_day_before = user.get('gomi_day_before', '(設定なし)')
        
        message = f'[設定内容]\n当日の通知時間 {gomi_today}\n前日の通知時間 {gomi_day_before}\n\n(※注意)\n通知は数分遅れて届く場合があります。あらかじめご了承ください。'
    else:
        message = '設定が取得できませんでした'
        
    push_message(user_id, message)
    

def set_notification_time(user_id, column_name, postback):
    """
    指定ユーザーの通知時間を設定して、結果を通知します

    Parameters
    ----------
    user_id : string
        ユーザーID
    column_name : string
        設定対象（gomi_today/gomi_day_beforeのどちらか、usersテーブル上のカラム名と同じにしています）
    postback : dictionary
        webhookで送られてきたpostback情報
    """
    if column_name == 'gomi_today' or column_name == 'gomi_day_before':
        new_value = postback['params']['time']
        print(new_value)
        
        result = dynamodb.set_column_to_users_table(user_id, column_name, new_value)
        
        if result:
            if column_name == 'gomi_today':
                message = f'当日の通知時間を{new_value}に設定しました'
            elif column_name == 'gomi_day_before':
                message = f'前日の通知時間を{new_value}に設定しました'
        else:
            message = '通知時間の設定に失敗しました'
            
        push_message(user_id, message)
    else:
        pass


def remove_notification_time(user_id, column_name):
    """
    指定ユーザーの通知時間の設定を削除して、結果を通知します

    Parameters
    ----------
    user_id : string
        ユーザーID
    column_name : string
        設定対象（gomi_today/gomi_day_beforeのどちらか、usersテーブル上のカラム名と同じにしています）
    """
    if column_name == 'gomi_today' or column_name == 'gomi_day_before':
        result = dynamodb.remove_column_from_users_table(user_id, column_name)
        
        if result:
            if column_name == 'gomi_today':
                message = f'当日の通知を停止しました'
            elif column_name == 'gomi_day_before':
                message = f'前日の通知を停止しました'
        else:
            message = '通知時間の設定に失敗しました'
            
        push_message(user_id, message)
    else:
        pass