from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import render

from apps.user.models import *


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = CustomUser.objects.get(username=username)
            if not user.is_active:
                return JsonResponse(status=404, data={'message': '帳號已被停用。'})
        except Exception as e:
            return JsonResponse(status=401, data={'message': '帳號或密碼錯誤。'})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            message = '登入成功'
        else:
            return JsonResponse(status=401, data={'message': '帳號或密碼錯誤。'})

        try:
            next = request.GET['next']
        except:
            next = '/'

        data = {
            'message': message,
            'next': next,
        }
        return JsonResponse(status=200, data=data)
    else:
        return render(request, 'users/login.html')


def user_logout(request):
    logout(request)
    return redirect('/')


def create_user_view(command_text, line_user):
    if CustomUser.objects.filter(line_uid=line_user.user_id, is_superuser=True).count() == 0:
        return ''

    list_params = command_text.strip().split(' ')
    if len(list_params) == 1:
        return f"請輸入要建立的帳號"
    else:
        username = list_params[1]

    if CustomUser.objects.filter(username=username).count() > 0:
        return f"此帳號「{username}」已存在"

    user = CustomUser.objects.create(username=username)
    password = user.set_password()
    user.save()
    return f"已建立帳號「{user}」，密碼為「{password}」"


def bind_line_user(command_text, line_user):
    list_params = command_text.strip().split(' ')
    if len(list_params) != 2:
        return f"指令為「綁定帳號 帳號」，例如：\n「綁定帳號 user001」"
    else:
        username = list_params[1]

    query_set = CustomUser.objects.filter(line_uid=line_user.user_id)
    if query_set.count() > 0:
        obj = query_set.first()
        return f"您的Line帳號已經綁定帳號「{obj.username}」"

    if CustomUser.objects.filter(username=username).count() > 0:
        return f"帳號「{username}」已存在，請更換一個帳號"

    user = CustomUser.objects.create(username=username, fullname=line_user.display_name, line_uid=line_user.user_id)
    password = user.set_password()
    user.save()
    return f"已建立帳號「{user}」並與您的Line帳號綁定"


def create_upload_token(line_user):
    try:
        user = CustomUser.objects.get(line_uid=line_user.user_id)
    except Exception as e:
        return f"請先綁定Line帳號"

    if user.allowed_upload == False:
        return f"沒有上傳檔案權限"

    query_set = AnyToken.objects.filter(user=user, name="UPLOAD_LOGIN", status=True)
    query_set.update(status=False, expire_time=timezone.now())

    obj_token = AnyToken.objects.create(user=user, name="UPLOAD_LOGIN", token=BaseUserManager().make_random_password(), status=True)
    return f"請透過以下網址上傳檔案：\nhttp://localhost:8000/coa/upload/?token={obj_token.token}"
