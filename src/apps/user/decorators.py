from django.contrib.auth import login, get_user_model
from django.shortcuts import redirect


def token_login(func):
    def wrap(request, *args, **kwargs):
        token = request.GET.get('token')
        if key is not None:
            user = get_user_model().objects.filter(line_user__key=key)
            if user.count() == 1:
                user = user.first()
                login(request, user)
                path = request.META.get('PATH_INFO')
                return redirect(path)
        return func(request, *args, **kwargs)
    return wrap
