import datetime
import json
import os
import random
import traceback

from linebot import (
    LineBotApi,
    WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models.events import (
    AccountLinkEvent,
    BeaconEvent,
    FollowEvent,
    JoinEvent,
    LeaveEvent,
    MemberJoinedEvent,
    MemberLeftEvent,
    MessageEvent,
    PostbackEvent,
    ThingsEvent,
    UnfollowEvent
)
from linebot.models.messages import (
    AudioMessage,
    FileMessage,
    ImageMessage,
    LocationMessage,
    StickerMessage,
    TextMessage,
    VideoMessage
)
from linebot.models.send_messages import (
    AudioSendMessage,
    ImageSendMessage,
    LocationSendMessage,
    SendMessage,
    StickerSendMessage,
    TextSendMessage,
    VideoSendMessage
)
from linebot.models.template import (
    ButtonsTemplate,
    CarouselTemplate,
    ConfirmTemplate,
    ImageCarouselTemplate,
    TemplateSendMessage
)
from linebot.exceptions import LineBotApiError

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.coa.views import (
    change_proxy,
    file_view_crop_produce,
    file_view_product_code,
    get_reply_from_text
)
from apps.coa.utils import CustomError
from apps.log.models import (
    LineCallBackLog,
    LineFollowLog,
    LineMessageLog,
    TracebackLog
)
from apps.user.views import (
    create_upload_token,
    create_user_view,
    bind_line_user
)

from .builder import build_line_user
from .models import (
    LineUser,
    SD
)
from .utils import parser_product


# LINE_BOT_API = LineBotApi('YOUR_CHANNEL_ACCESS_TOKEN')
# HANDLER = WebhookHandler('YOUR_CHANNEL_SECRET')
if settings.LINE_TEST_MODE:
    LINE_CHANNEL_ACCESS_TOKEN = settings.LINE_CHANNEL_ACCESS_TOKEN_TEST
    LINE_CHANNEL_SECRET = settings.LINE_CHANNEL_SECRET_TEST
else:
    LINE_CHANNEL_ACCESS_TOKEN = settings.LINE_CHANNEL_ACCESS_TOKEN
    LINE_CHANNEL_SECRET = settings.LINE_CHANNEL_SECRET


LINE_BOT_API = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN, timeout=60)
HANDLER = WebhookHandler(LINE_CHANNEL_SECRET)


@csrf_exempt
def home(request):
    return HttpResponse('Hi!')


@csrf_exempt
def callback(request):
    try:
        signature = request.headers.get('X-Line-Signature', '')
        body = request.body.decode('utf-8')
        build_line_user(LINE_BOT_API, body)
        HANDLER.handle(body, signature)
        return HttpResponse(status=200, content='OK')
    except InvalidSignatureError:
        LineCallBackLog.objects.create(signature=signature, body=body, message=response)
        response = 'Invalid signature. Please check your channel access token/channel secret.'
        return HttpResponse(status=400, content=response)
    except Exception:
        log = LineCallBackLog.objects.create(signature=signature, body=body, message=traceback.format_exc())
        return HttpResponse(status=400, content=f"未知錯誤，錯誤編號「{log.id}」，請至後台查詢詳細記錄。")


@HANDLER.add(FollowEvent)
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
    except Exception:
        log.reply = traceback.format_exc()
        log.status = False
        log.save()


@HANDLER.add(UnfollowEvent)
def handle_unfollow(event):
    user_id = event.source.user_id
    user = LineUser.objects.get(user_id=user_id)
    try:
        log = LineFollowLog.objects.create(user=user, message='封鎖')
        user.status = False
        user.save()
    except Exception:
        log.reply = traceback.format_exc()
        log.status = False
        log.save()


@HANDLER.add(MessageEvent, message=TextMessage)
def handle_message_text(event):
    try:
        message_id = event.message.id
        reply_token = event.reply_token
        text = event.message.text
        start_timestamp = event.timestamp / 1000
        user_id = event.source.user_id
        user = LineUser.objects.get(user_id=user_id)
    except Exception as e:
        traceback_log = TracebackLog.objects.create(app='handle_message_text', message=traceback.format_exc())
        reply = f"發生錯誤，錯誤訊息編號「{traceback_log.id}」，請通知管理員處理。"
        try:
            LINE_BOT_API.reply_message(reply_token, TextSendMessage(text=reply))
        except Exception:
            TracebackLog.objects.create(app='handle_message_text', message=traceback.format_exc())

    try:
        line_log = LineMessageLog.objects.create(**{
            'user': user,
            'message_id': message_id,
            'reply_token': reply_token,
            'message': text,
            'timestamp': start_timestamp,
            'method': 'reply',
            'status': False
        })

        if text.startswith('建立帳號'):
            reply = create_user_view(text, user)
        elif text.startswith('綁定帳號'):
            reply = bind_line_user(text, user)
        elif text.startswith('上傳檔案'):
            reply = create_upload_token(user)
        elif text.startswith('未讀訊息'):
            reply = '開發中...'
        # elif text.startswith('更換代理'):
        #     reply = change_proxy(text, user)
        else:
            reply = get_reply_from_text(text).strip()

        line_log.reply = reply
        line_log.status = True
        update_fields = ['reply', 'status']
    except CustomError as ce:
        reply = str(ce)
        line_log.reply = reply
        update_fields = ['reply']
    except Exception:
        traceback_log = TracebackLog.objects.create(app='handle_message_text', message=traceback.format_exc())
        reply = f"發生錯誤，訊息編號「{line_log.id}」，錯誤訊息編號「{traceback_log.id}」，請通知管理員處理。"
        line_log.reply = reply
        update_fields = ['reply']
    finally:
        line_log.save(update_fields=update_fields)

    try:
        # end_at = datetime.datetime.now()
        LINE_BOT_API.reply_message(reply_token, TextSendMessage(text=reply))
    except LineBotApiError:
        try:
            LINE_BOT_API.push_message(user_id, TextSendMessage(text=reply))
            line_log.method = 'push'
            line_log.save(update_fields=['method'])
        except Exception:
            TracebackLog.objects.create(app='handle_message_text_push', message=traceback.format_exc())
            line_log.status = False
            line_log.save(update_fields=['status'])
    except Exception:
        TracebackLog.objects.create(app='handle_message_text_reply', message=traceback.format_exc())
        line_log.status = False
        line_log.save(update_fields=['status'])


@HANDLER.add(MessageEvent, message=StickerMessage)
def handle_message_sticker(event):
    message_id = event.message.id
    reply_token = event.reply_token
    sticker_id = event.message.sticker_id
    user_id = event.source.user_id
    user = LineUser.objects.get(user_id=user_id)
    name = user.display_name
    reply_list = ['不想理你', f"{name}別鬧", f"{name}不要玩機器人", f"{name}你想跟我貼圖Battle？", "...", f"{name}快去調查！"]
    reply = f"{random.choice(reply_list)}"
    log = LineMessageLog.objects.create(
        user=user, message_id=message_id, reply_token=reply_token, message=f"貼圖：{sticker_id}", reply=reply
    )
    LINE_BOT_API.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )


@HANDLER.add(MessageEvent, message=FileMessage)
def handle_message_file(event):
    try:
        message_id = event.message.id
        file_name = event.message.file_name
        file_size = event.message.file_size
        reply_token = event.reply_token
        user_id = event.source.user_id
        user = LineUser.objects.get(user_id=user_id)

        line_log = LineMessageLog.objects.create(**{
            'user': user,
            'message_id': message_id,
            'reply_token': reply_token,
            'message': f"上傳檔案，檔案名稱：{file_name}，檔案大小：{file_size}"
        })

        if '主力' in file_name or '勞動力' in file_name or  '產值' in file_name or '產量' in file_name:
            # 主力勞動力代碼對照_timestamp.xlsx
            # 產量產值總表_timestamp.xlxl
            path = f"{file_name.split('.')[0]}_{int(datetime.datetime.now().timestamp())}.{file_name.split('.')[-1]}"
            message_content = LINE_BOT_API.get_message_content(message_id)
            with open(path, 'wb') as fd:
                for chunk in message_content.iter_content():
                    fd.write(chunk)
        else:
            reply = f"上傳的檔案名稱「{file_name}」不符要求，上傳失敗！"
            line_log.reply = reply
            line_log.save(update_fields=['reply'])
            LINE_BOT_API.reply_message(reply_token, TextSendMessage(text=reply))
            # ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__',
            # '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__',
            # '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__',
            # '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__',
            # '__str__', '__subclasshook__', '__weakref__', 'content', 'content_type', 'iter_content', 'response']
            # message_content <linebot.models.responses.Content object at 0x107e460f0>

        if '主力' in file_name or '勞動力' in file_name:
            reply = file_view_product_code(path)
        else:
            reply = file_view_crop_produce(path)
        os.remove(path)
        line_log.reply = reply
        line_log.save(update_fields=['reply'])
        LINE_BOT_API.reply_message(reply_token, TextSendMessage(text=reply))
    except Exception:
        reply = f"發生錯誤，錯誤訊息編號「{line_log.id}」，請通知工程師處理。"
        line_log.reply = traceback.format_exc()
        line_log.status = False
        line_log.save(update_fields=['reply', 'status'])
        LINE_BOT_API.reply_message(reply_token, TextSendMessage(text=reply))
