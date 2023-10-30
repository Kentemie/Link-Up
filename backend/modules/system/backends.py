from typing import Any

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.http.request import HttpRequest


UserModel = get_user_model()


class UserModelBackend(ModelBackend):
    """
     Authorization override
    """

    def authenticate(self, request: HttpRequest, username: str | None = ..., password: str | None = ..., **kwargs: Any) -> AbstractBaseUser | None:
        try:
            user = UserModel.objects.get(Q(username=username) | Q(email__iexact=username))
        except UserModel.DoesNotExist:
            return None
        except MultipleObjectsReturned:
            return UserModel.objects.filter(email=username).order_by('id').first()
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
            
    def get_user(self, user_id: int) -> AbstractBaseUser | None:
        try:
            user = UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
        
        return user if self.user_can_authenticate(user) else None