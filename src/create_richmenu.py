import os

from linebot import LineBotApi
from linebot.models import RichMenu, RichMenuArea, RichMenuBounds, RichMenuSize
from linebot.models import MessageAction, URIAction, PostbackAction, DatetimePickerAction

def handler(event, context):
    """
    リッチメニューを作成します

    使用するサンプル画像は files/richmenu_tmp.png にあります（必要に応じて差し替えてください）
    コード中の座標・サイズの数値は、サンプル画像に合わせた数値となっています
    """

    line_bot_api = LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])

    # リッチメニューの作成
    rich_menu_to_create = RichMenu(
        size=RichMenuSize(width=2500, height=1658),
        selected=False,
        name="tmp richmenu",
        chat_bar_text="メニューはこちらをタップ",
        areas=[
            # 設定時間の確認
            RichMenuArea(
                bounds=RichMenuBounds(x=133, y=350, width=1400, height=300),
                action=PostbackAction(
                    display_text=None, 
                    label='設定時間の確認', 
                    data='action=check'
                )
            ),
            # 当日の通知時間（設定）
            RichMenuArea(
                bounds=RichMenuBounds(x=0, y=1033, width=625, height=625),
                action=DatetimePickerAction(
                    label='gomi_today', 
                    data='action=set&target=gomi_today', 
                    mode='time', 
                    initial='07:00', 
                    max='07:59', 
                    min='00:00'
                )
            ),
            # 当日の通知時間（削除）
            RichMenuArea(
                bounds=RichMenuBounds(x=625, y=1033, width=625, height=625),
                action=PostbackAction(
                    display_text=None, 
                    label='Postback action', 
                    data='action=remove&target=gomi_today'
                )
            ),
            # 前日の通知時間（設定）
            RichMenuArea(
                bounds=RichMenuBounds(x=1250, y=1033, width=625, height=625),
                action=DatetimePickerAction(
                    label='gomi_day_before', 
                    data='action=set&target=gomi_day_before', 
                    mode='time', 
                    initial='18:00', 
                    max='23:59', 
                    min='16:00'
                )
            ),
            # 前日の通知時間（削除）
            RichMenuArea(
                bounds=RichMenuBounds(x=1875, y=1033, width=625, height=625),
                action=PostbackAction(
                    display_text=None, 
                    label='Postback action', 
                    data='action=remove&target=gomi_day_before'
                )
            ),
            # フリースペース（例: テキストを出すだけ）
            RichMenuArea(
                bounds=RichMenuBounds(x=1667, y=0, width=833, height=833),
                action=MessageAction(label='hogehoge', text='hogehoge') 
            ),
            # フリースペース（例: アプリ内ブラウザで指定URLにアクセス）
            RichMenuArea(
                bounds=RichMenuBounds(x=1667, y=0, width=833, height=833),
                action=URIAction(label='URI', uri='https://heptagon.co.jp/')
            ),
        ]
    )

    new_richmenu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)

    # リッチメニュー用の画像をアップロード
    with open('files/richmenu_tmp.png', 'rb') as f:
        line_bot_api.set_rich_menu_image(new_richmenu_id, 'image/png', f)

    # リッチメニューをデフォルトに
    line_bot_api.set_default_rich_menu(new_richmenu_id)

    # デフォルトのリッチメニュー以外は削除する
    menu_list = line_bot_api.get_rich_menu_list()

    for menu in menu_list:
        if menu.rich_menu_id != new_richmenu_id:
            line_bot_api.delete_rich_menu(menu.rich_menu_id)

    return {
        "rich_menu_id": new_richmenu_id
    }