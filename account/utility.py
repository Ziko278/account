from django.http import HttpResponse
import random
from django.core.mail import EmailMessage, send_mail
from account.forms import *
from account.models import *
from django.contrib.auth.models import User
from django.core.mail import EmailMessage, send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.core.exceptions import PermissionDenied
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings


def verification_code_mail(request, code, email):

    context = {
        'domain': get_current_site(request),
        'code': code,
        'email': email,
    }
    mail_subject = 'Providus Bank Email Verification'
    from_email = settings.EMAIL_HOST_USER
    html_message = render_to_string('message/verify_email.html', context)
    plain_message = strip_tags(html_message)

    mail_sent = send_mail(mail_subject, plain_message, from_email, [email], html_message=html_message,
                          fail_silently=True)
    return mail_sent


def verification_code(request, email):
    mail_exist = User.objects.filter(username=email)
    if mail_exist:
        return HttpResponse('Email Already Exists')
    code_exist = VerificationCodeModel.objects.filter(email=email).first()
    if code_exist:
        code_exist.status = 'inactive'
        code_exist.save()
    code = random.randint(100000, 999999)
    create_code = VerificationCodeModel.objects.create(code=code, email=email, status='active')
    create_code.save()

    email_sent = verification_code_mail(request, code, email)
    if email_sent:
        return HttpResponse('Verification Code Sent')
    return HttpResponse('An error occurred, Try again')
