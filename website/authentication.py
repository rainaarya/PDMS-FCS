from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User

class SettingsBackend(BaseBackend):

    def authenticate(self, request, username=None, password=None):
        login_valid = User.objects.filter(username=username).exists()
        pwd_valid = False
        if login_valid:
            pwd_valid = check_password(password, User.objects.get(username=username).password)
        if login_valid and pwd_valid:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None