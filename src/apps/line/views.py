import json
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

from apps.coa.utils import pre_process_text
from apps.log.models import LineMessageLog, LineFollowLog

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
        return HttpResponse(status=400, content=response)

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

        if '產地' in text or '批發' in text or '零售' in text:
            result = parser_product(text)
            reply = TextSendMessage(text=result)
        elif text.startswith('1'):
            reply = pre_process_text(text)
            if reply is False:
                reply = '請輸入年+空格+關鍵字\n例如：\n107 產值 總產值\n107 產值 豬\n107 農家所得\n107 農牧戶\n107 耕地面積'
            reply = TextSendMessage(text=reply)
        else:
            reply = TextSendMessage(text="請輸入產品+空格+產地/批發/零售\n例如：芒果 產地")

        log.reply = reply
        log.save()
        line_bot_api.reply_message(reply_token, reply)
    except Exception as e:
        reply = TextSendMessage(text=f"發生錯誤，錯誤訊息編號「{log.id}」，請通知工程師處理。")
        log.reply = traceback.format_exc()
        log.status = False
        log.save()
        line_bot_api.reply_message(reply_token, reply)


@handler.add(MessageEvent, message=StickerMessage)
def handle_message_sticker(event):
    print(event.as_json_dict())
    print('MessageEvent StickerMessage')
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="Hello, world")
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
