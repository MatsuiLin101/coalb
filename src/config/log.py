import requests

from django.conf import settings
from django.utils.log import AdminEmailHandler
from django.urls import reverse


class ProxyAdminEmailHandler(AdminEmailHandler):

    def send_mail(self, subject, message, *args, **kwargs):
        proxy_domain = settings.PROXY_DOMAIN
        url = proxy_domain + reverse('log:proxy_send_email')
        data = {
            'token': settings.PROXY_TOKEN,
            'subject': subject,
            'message': message
        }
        res = requests.post(url, data=data)
