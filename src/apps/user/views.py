from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import render

from apps.user.models import CustomUser


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


def create_user_view(command_text):
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
