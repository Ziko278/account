from django.urls import path
from account.views import *


urlpatterns = [
    path('register', user_signup_view, name='signup'),
    path('register/success', user_signup_done_view, name='signup_done'),
    path('dashboard', dashboard_view, name='dashboard'),
    path('login', user_signin_view, name='login'),
    path('logout', user_signout_view, name='logout'),
    path('verify-email/<str:uidb64>/<str:token>/', verify_email, name='verify_email'),

]

