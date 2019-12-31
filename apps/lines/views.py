import json

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

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from .models import SD
from .utils import parser_product


# line_bot_api = LineBotApi('YOUR_CHANNEL_ACCESS_TOKEN')
# handler = WebhookHandler('YOUR_CHANNEL_SECRET')
line_bot_api = LineBotApi('ActG2d3ixqDGVUhN5XfSY3R4Y45Z4GU8c957CuLU7BvJYVzB+M4pgKjTSbzU/IwToBOW0v/od0ciXX2o7zuh809P68S32ZrvAUtS7RoRqSIn7cWgJZYrWGc4ToTdRcjy7+j7BcmYhlwm+yPoc7WthwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('cee5f9aa47f1c46beeb2c7b2016843fb')


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
        handler.handle(body, signature)
        print('handler ok')
    except InvalidSignatureError:
        print('handler error')
        response = 'Invalid signature. Please check your channel access token/channel secret.'
        return HttpResponse(status=400, content=response)

    return HttpResponse(status=200, content='OK')


@handler.add(MessageEvent, message=TextMessage)
def handle_message_text(event):
    text = event.message.text
    print(f'MessageEvent TextMessage: {text}')

    # if text == '選單':
    #     category = SD.objects.filter(layer=None, parent=None)
    #
    #     template = ButtonsTemplate(
    #         title = '選單',
    #         text = '請選擇要查的資料',
    #         actions = [{
    #             'type': 'postback',
    #             'label': category.get(id=18).name,
    #             'data': f"id={category.get(id=18).id}, layer=1",
    #         }, {
    #             'type': 'postback',
    #             'label': category.get(id=25).name,
    #             'data': f"id={category.get(id=25).id}, layer=1",
    #         }]
    #     )
    #     print(template)
    #
    #     reply = TemplateSendMessage(
    #         alt_text = 'Buttons template',
    #         template = template
    #     )
    if '產地' in text or '批發' in text:
        result = parser_product(text)
        print('5')
        reply = TextSendMessage(text=result)
    else:
        reply = TextSendMessage(text="請輸入產品+空格+產地/批發/零售\n例如：芒果 產地")

    line_bot_api.reply_message(event.reply_token, reply)


@handler.add(MessageEvent, message=StickerMessage)
def handle_message_sticker(event):
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
