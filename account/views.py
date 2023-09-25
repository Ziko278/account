from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template import RequestContext
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.urls import reverse
import random
from django.contrib.auth.models import User
from account.utility import verification_code
from account.models import VerificationCodeModel, UserProfileModel
from account.forms import LoginForm
from django.contrib.messages.views import SuccessMessageMixin, messages

from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.core.mail import send_mail


class UserDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'user_dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


@csrf_exempt
def user_signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if request.POST['username'] and request.POST['email']:
            username = request.POST['username']
            email = request.POST['email']

            user_exist = User.objects.filter(username=username).count()
            if user_exist > 0:
                messages.error(request, 'Username Already Exist')
            else:
                full_name = request.POST['full_name']
                password = request.POST['password']

                user = User.objects.create_user(username, email, password)
                user.is_active = False
                user.save()

                if user.id:
                    account_number = "20" + str(random.randint(10000000, 99999999))
                    profile = UserProfileModel.objects.create(user=user, full_name=full_name,
                                                              account_number=account_number, account_balance=0)
                    profile.save()

                    send_verification_email(request, user.id)
                    request.session['signup'] = True
                    return redirect('signup_done')

        else:
            messages.error(request, 'Please crosscheck details')

    else:
        form = UserCreationForm()

    context = {
        'form': form
    }
    return render(request, 'account/register.html')


@csrf_exempt
def user_signup_done_view(request):
    if request.session.get('signup', None):
        del request.session['signup']
        return render(request, 'account/register_done.html')
    else:
        return redirect(reverse('login'))


@csrf_exempt
def user_signin_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, 'Welcome Back {}'.format(user.username))
                    if 'remember_login' not in request.POST:
                        request.session.set_expiry(0)
                        request.session.modified = True

                    nxt = request.GET.get("next", None)
                    if nxt:
                        return redirect(request.GET.get('next'))
                    return redirect(reverse('dashboard'))
                else:
                    messages.error(request, 'Account not Active')
            else:
                messages.error(request, 'Invalid Credentials')
        else:
            messages.error(request, 'Invalid Credentials')
    else:
        form = LoginForm()

    context = {
        'form': form
    }
    return render(request, 'account/login.html', context)


User = get_user_model()


def send_verification_email(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return HttpResponse("User not found")

    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token_encoded = urlsafe_base64_encode(force_bytes(token))

    verification_url = f"{get_current_site(request).domain}/verify-email/{uid}/{token_encoded}/"

    subject = "Verify Your Email"
    message = render_to_string(
        "account/verification_email.html",
        {"user": user, "verification_url": verification_url},
    )

    from_email = "odekeziko@gmail.com"  # Replace with your email
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list, html_message=message)


def verify_email(request, uidb64, token):
    try:
        uid = str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        # Mark the email as verified
        user.email_verified = True
        user.save()

        # Redirect to the email verification success page
        messages.success(request, 'account verified successfully')
        return redirect(reverse('login'))
    else:
        # Redirect to the email verification failure page
        messages.error(request, 'failed to verify account')
        return redirect(reverse('login'))


def user_signout_view(request):
    logout(request)
    return redirect(reverse('login'))


def dashboard_view(request):
    return render(request, 'account/dashboard.html')


