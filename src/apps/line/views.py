import datetime
import json
import os
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

from apps.log.models import TracebackLog

from apps.coa.views import api_view, file_view_product_code, file_view_crop_produce
from apps.coa.utils import CustomError
from apps.log.models import LineMessageLog, LineFollowLog, LineCallBackLog
from apps.user.views import (
    create_user_view,
    bind_line_user,
    create_upload_token,
)

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

        if text.startswith('建立帳號'):
            reply = create_user_view(text, user)
        elif text.startswith('綁定帳號'):
            reply = bind_line_user(text, user)
        elif text.startswith('上傳檔案'):
            reply = create_upload_token(user)
        else:
            reply = api_view(text).strip()
        log.reply = reply
        log.save()
    except CustomError as ce:
        reply = str(ce)
        log.reply = reply
        log.save()
    except Exception as e:
        traceback_log = TracebackLog.objects.create(app="handle_message_text", message=traceback.format_exc())
        reply = f"發生錯誤，訊息編號「{log.id}」，錯誤訊息編號「{traceback_log.id}」，請通知管理員處理。"
        log.reply = reply
        log.status = False
        log.save()

    try:
        message = line_bot_api.reply_message(reply_token, TextSendMessage(text=reply))
    except Exception as e:
        traceback_log = TracebackLog.objects.create(app="handle_message_text_reply_message", message=traceback.format_exc())


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
        user=user, message_id=message_id, reply_token=reply_token, message=f"貼圖：{sticker_id}", reply=reply
    )
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )


@handler.add(MessageEvent, message=FileMessage)
def handle_message_file(event):
    try:
        message_id = event.message.id
        file_name = event.message.file_name
        file_size = event.message.file_size
        reply_token = event.reply_token
        user_id = event.source.user_id
        user = LineUser.objects.get(user_id=user_id)

        log = LineMessageLog.objects.create(
            user=user, message_id=message_id, reply_token=reply_token, message=f"上傳檔案，檔案名稱：{file_name}，檔案大小：{file_size}"
        )

        if "主力" in file_name or "勞動力" in file_name or  "產值" in file_name or "產量" in file_name:
            # 主力勞動力代碼對照_timestamp.xlsx
            # 產量產值總表_timestamp.xlxl
            path = f"{file_name.split('.')[0]}_{int(datetime.datetime.now().timestamp())}.{file_name.split('.')[-1]}"
            message_content = line_bot_api.get_message_content(message_id)
            with open(path, 'wb') as fd:
                for chunk in message_content.iter_content():
                    fd.write(chunk)
        else:
            reply = f'上傳的檔案名稱「{file_name}」不符要求，上傳失敗！'
            log.reply = reply
            log.save()
            line_bot_api.reply_message(reply_token, TextSendMessage(text=reply))
            # ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__',
            # '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__',
            # '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__',
            # '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__',
            # '__str__', '__subclasshook__', '__weakref__', 'content', 'content_type', 'iter_content', 'response']
            # message_content <linebot.models.responses.Content object at 0x107e460f0>

        if "主力" in file_name or "勞動力" in file_name:
            reply = file_view_product_code(path)
        else:
            reply = file_view_crop_produce(path)
        os.remove(path)
        log.reply = reply
        log.save()
        line_bot_api.reply_message(reply_token, TextSendMessage(text=reply))
    except Exception as e:
        reply = f"發生錯誤，錯誤訊息編號「{log.id}」，請通知工程師處理。"
        log.reply = traceback.format_exc()
        log.status = False
        log.save()
        line_bot_api.reply_message(reply_token, TextSendMessage(text=reply))
