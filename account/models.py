from django.db import models
from django.contrib.auth.models import User


class UserProfileModel(models.Model):
    full_name = models.CharField(max_length=200)
    account_number = models.CharField(max_length=20, blank=True, null=True)
    account_balance = models.FloatField(default=0, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.full_name.upper()


class EmailModel(models.Model):
    email = models.EmailField()


class VerificationCodeModel(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=10)
    status = models.CharField(max_length=20)

