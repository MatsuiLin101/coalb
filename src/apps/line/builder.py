import json

from apps.log.models import LineBodyLog
from apps.line.models import LineUser


def build_line_user(line_bot_api, body):
    '''
    檢查line user_id是否存在資料庫
    若不存在就新增Line使用者
    '''
    user_id = json.loads(body)['events'][0]['source']['userId']
    try:
        user = LineUser.objects.get(user_id=user_id)
    except Exception as e:
        profile = line_bot_api.get_profile(user_id)
        display_name = profile.display_name
        picture_url = profile.picture_url
        status_message = profile.status_message
        language = profile.language
        user = LineUser.objects.create(
            user_id=user_id, display_name=display_name, picture_url=picture_url,
            status_message=status_message, language=language, status=True
        )
    log = LineBodyLog.objects.create(user=user, body=body)
