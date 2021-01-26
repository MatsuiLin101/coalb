import json
import random
import traceback

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models.events import (
    MessageEvent,
    FollowEvent,
    UnfollowEvent,
    JoinEvent,
    LeaveEvent,
    PostbackEvent,
    AccountLinkEvent,
    MemberJoinedEvent,
    MemberLeftEvent,
    BeaconEvent,
    ThingsEvent,
)
from linebot.models.messages import (
    TextMessage,
    ImageMessage,
    VideoMessage,
    AudioMessage,
    LocationMessage,
    StickerMessage,
    FileMessage
)
from linebot.models.send_messages import (
    SendMessage,
    TextSendMessage,
    ImageSendMessage,
    VideoSendMessage,
    AudioSendMessage,
    LocationSendMessage,
    StickerSendMessage,
)
from linebot.models.template import (
    TemplateSendMessage,
    ButtonsTemplate,
    CarouselTemplate,
    ConfirmTemplate,
    ImageCarouselTemplate,
)

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from apps.coa.utils import (
    pre_process_text_2,
    query_produce_value,
    query_produce_value_product,
)
from apps.log.models import LineMessageLog, LineFollowLog, LineCallBackLog

from .models import LineUser, SD
from .utils import parser_product
from .builder import build_line_user


# line_bot_api = LineBotApi('YOUR_CHANNEL_ACCESS_TOKEN')
# handler = WebhookHandler('YOUR_CHANNEL_SECRET')
if settings.LINE_TEST_MODE:
    line_channel_access_token = settings.LINE_CHANNEL_ACCESS_TOKEN_TEST
    line_channel_secret = settings.LINE_CHANNEL_SECRET_TEST
else:
    line_channel_access_token = settings.LINE_CHANNEL_ACCESS_TOKEN
    line_channel_secret = settings.LINE_CHANNEL_SECRET


line_bot_api = LineBotApi(line_channel_access_token, timeout=60)
handler = WebhookHandler(line_channel_secret)


@csrf_exempt
def home(request):
    data = request.POST.dict()
    # print(data)
    for k, v in data.items():
        print(f'{k} ### {v}\n\n')
    return HttpResponse('Hi!')


@csrf_exempt
def callback(request):
    try:
        signature = request.headers['X-Line-Signature']
        body = request.body.decode('utf-8')
        build_line_user(line_bot_api, body)
        handler.handle(body, signature)
    except InvalidSignatureError:
        response = 'Invalid signature. Please check your channel access token/channel secret.'
        log = LineCallBackLog.objects.create(signature=signature, body=body, message=response)
        return HttpResponse(status=400, content=response)
    except Exception as e:
        message = traceback.format_exc()
        log = LineCallBackLog.objects.create(signature=signature, body=body, message=message)
        return HttpResponse(status=400, content="未知錯誤，請至後台查詢詳細記錄。")

    return HttpResponse(status=200, content='OK')


@handler.add(FollowEvent)
def handle_follow(event):
    reply_token = event.reply_token
    user_id = event.source.user_id
    user = LineUser.objects.get(user_id=user_id)
    try:
        log = LineFollowLog.objects.create(
            user=user, reply_token=reply_token, message='加入好友'
        )
        user.status = True
        user.save()
    except Exception as e:
        log.reply = traceback.format_exc()
        log.status = False
        log.save()


@handler.add(UnfollowEvent)
def handle_unfollow(event):
    user_id = event.source.user_id
    user = LineUser.objects.get(user_id=user_id)
    try:
        log = LineFollowLog.objects.create(user=user, message='封鎖')
        user.status = False
        user.save()
    except Exception as e:
        log.reply = traceback.format_exc()
        log.status = False
        log.save()


@handler.add(MessageEvent, message=TextMessage)
def handle_message_text(event):
    message_id = event.message.id
    reply_token = event.reply_token
    text = event.message.text
    user_id = event.source.user_id
    user = LineUser.objects.get(user_id=user_id)
    try:
        log = LineMessageLog.objects.create(
            user=user, message_id=message_id, reply_token=reply_token, message=text
        )

        # 將輸入的文字依據空格分割
        text_list = text.split(' ')
        if len(text_list) == 2:
            command, year = text_list
            city_product = None
            product = None
        elif len(text_list) == 3:
            command, year, city_product = text_list
            city = None
        elif len(text_list) == 4:
            command, year, city, city_product = text_list
        else:
            command = None
            year = None
            city = None
            city_product = None

        # 判斷分割後的第一組文字是哪一個指令
        if command == "總產值":
            response = query_produce_value(year, city_product)
            reply = f"{text}\n{response}"
        elif command == "產值":
            response = query_produce_value_product(year, city_product, city)
            reply = f"{text}\n{response}"
        elif '產地' in text or '批發' in text or '零售' in text:
            reply = parser_product(text)
        elif command == "農家所得" or command == "農牧戶" or command == "耕地面積":
            response = pre_process_text_2(command, year)
            reply = f"{text}\n{response}"
            # if reply is False:
            #     reply = '請輸入年+空格+關鍵字\n例如：\n107 產值 總產值\n107 產值 豬\n107 農家所得\n107 農牧戶\n107 耕地面積'
        elif "指令" in text:
            reply = f"目前提供的指令如下(括號內請改成要查詢的內容，並將底線以空白一格替換)：\n"
            reply += "總產值_(年份)\n"
            reply += "總產值_(年份)_(城市)\n"
            reply += "產值_(年份)_(農產品/畜產品)\n"
            reply += "產值_(年份)_(城市)_(農產品/畜產品)\n"
            reply += "農家所得_(年份)\n"
            reply += "農牧戶_(年份)\n"
            reply += "耕地面積_(年份)\n"
        else:
            reply = f"很抱歉，您輸入的指令「{text}」可能有誤，無法為您查詢，目前可使用的查詢指令如下(括號內請改成要查詢的內容，並將底線以空白一格替換)：\n"
            reply += "總產值_(年份)\n"
            reply += "總產值_(年份)_(城市)\n"
            reply += "產值_(年份)_(農產品/畜產品)\n"
            reply += "產值_(年份)_(城市)_(農產品/畜產品)\n"
            reply += "農家所得_(年份)\n"
            reply += "農牧戶_(年份)\n"
            reply += "耕地面積_(年份)\n"

        reply = reply.strip()
        log.reply = reply
        log.save()
        line_bot_api.reply_message(reply_token, TextSendMessage(text=reply))
    except Exception as e:
        reply = f"發生錯誤，錯誤訊息編號「{log.id}」，請通知工程師處理。"
        log.reply = traceback.format_exc()
        log.status = False
        log.save()
        line_bot_api.reply_message(reply_token, TextSendMessage(text=reply))


@handler.add(MessageEvent, message=StickerMessage)
def handle_message_sticker(event):
    message_id = event.message.id
    reply_token = event.reply_token
    sticker_id = event.message.sticker_id
    user_id = event.source.user_id
    user = LineUser.objects.get(user_id=user_id)
    name = user.display_name
    reply_list = ["不想理你", f"{name}別鬧", f"{name}不要玩機器人", f"{name}你想跟我貼圖Battle？", "...", f"{name}快去調查！"]
    reply = f"{random.choice(reply_list)}"
    log = LineMessageLog.objects.create(
        user=user, message_id=message_id, reply_token=reply_token, message=sticker_id, reply=reply
    )
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )


# @handler.add(PostbackEvent)
# def handle_postback(event):
#     data = event.postback.data.split(",")
#     print(f'PostbackEvent TextMessage {data}')
#     id = int(data[0].replace("id=", ""))
#     print(id)
#     layer = int(data[1].replace("layer=", ""))
#     print(layer)
#
#     options = SD.objects.get(id=id).sd_set.filter(layer=layer)
#     print('options ok')
#     actions = list()
#     for obj in options[:5]:
#         actions.append({
#             'type': 'postback',
#             'label': obj.name,
#             'data': f"id={obj.id}, layer={layer + 1}",
#         })
#     print('actions ok', actions)
#
#     template = ButtonsTemplate(
#         title = f"分類{layer}",
#         text = "請選擇分類",
#         # actions = [{
#         #     'type': 'postback',
#         #     'label': options.first().name,
#         #     'data': f"id={options.first().id}, layer=2"
#         # }, {
#         #     'type': 'postback',
#         #     'label': options.last().name,
#         #     'data': f"id={options.last().id}, layer=2"
#         # }]
#         actions = actions
#     )
#     print('template ok', template)
#
#     reply = TemplateSendMessage(
#         alt_text = 'Buttons template',
#         template = template
#     )
#     print(f'reply ok = {reply}')
#
#     print(f'reply_token = {event.reply_token}')
#     line_bot_api.reply_message(event.reply_token, reply)
