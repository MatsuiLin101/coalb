import json

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

# line_bot_api = LineBotApi('YOUR_CHANNEL_ACCESS_TOKEN')
# handler = WebhookHandler('YOUR_CHANNEL_SECRET')
line_bot_api = LineBotApi('ActG2d3ixqDGVUhN5XfSY3R4Y45Z4GU8c957CuLU7BvJYVzB+M4pgKjTSbzU/IwToBOW0v/od0ciXX2o7zuh809P68S32ZrvAUtS7RoRqSIn7cWgJZYrWGc4ToTdRcjy7+j7BcmYhlwm+yPoc7WthwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('cee5f9aa47f1c46beeb2c7b2016843fb')


def home(request):
    return HttpResponse('Hi!')

# @require_http_methods(["GET", "POST"])
@csrf_exempt
def callback(request):

    try:
        signature = request.headers['X-Line-Signature']
        body = request.body.decode('utf-8')
        print('signature = ', signature)
        print('body = ', json.loads(body))
        hook = handler.handle(body, signature)
        print(hook)
    except InvalidSignatureError:
        response = 'Invalid signature. Please check your channel access token/channel secret.'
        return HttpResponse(status=400, content=response)

    # return HttpResponse(status=200, content='OK')


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
    )
