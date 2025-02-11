from django.conf import settings
from django.core.mail import mail_admins
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound
)
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def proxy_send_email(request):
    if request.method != 'POST':
        return HttpResponseNotFound('<h1>Page not found</h1>')

    token = request.POST.get('token')
    subject = request.POST.get('subject')
    message = request.POST.get('message')

    if token != settings.PROXY_TOKEN:
        return HttpResponseNotFound('<h1>Page not found</h1>')

    try:
        mail_admins(subject, message, fail_silently=True)
        return HttpResponse('<h1>Success</h1>')
    except Exception as e:
        return HttpResponseBadRequest('<h1>Fail</h1>')
