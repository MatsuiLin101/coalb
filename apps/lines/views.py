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

    if text == '選單':
        category = SD.objects.filter(layer=None, parent=None)

        template = ButtonsTemplate(
            title = '選單',
            text = '請選擇要查的資料',
            actions = [{
                'type': 'postback',
                'label': category.get(id=18).name,
                'data': f"id={category.get(id=18).id}, lay=1",
            }, {
                'type': 'postback',
                'label': category.get(id=25).name,
                'data': f"id={category.get(id=25).id}, lay=1",
            }]
        )
        print(template)

        reply = TemplateSendMessage(
            alt_text = 'Buttons template',
            template = template
        )
    else:
        reply = TextSendMessage(text=text)

    line_bot_api.reply_message(event.reply_token, reply)


@handler.add(MessageEvent, message=StickerMessage)
def handle_message_sticker(event):
    print('MessageEvent StickerMessage')
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="Hello, world")
    )


@handler.add(PostbackEvent)
def handle_postback(event):
    print(f'PostbackEvent TextMessage {data}')
    data = event.postback.data.split[","]
    id = int(data[0].replace("id=", ""))
    lay = int(data[1].replace("lay=", ""))

    options = SD.objects.get(id=id).sd_set.filter(lay=lay)
    actions = list()
    for obj in options:
        actions.append({
            'type': 'postback',
            'label': obj.name,
            'data': f"id=obj.id, lay={lay + 1}",
        })

    template = ButtonsTemplate(
        title = f"分類{lay}",
        text = "請選擇分類",
        actions = actions
    )

    line_bot_api.reply_message(
        event.reply_token,
        TemplateSendMessage(
            alt_text = 'Buttons template',
            template = template
        )
    )
