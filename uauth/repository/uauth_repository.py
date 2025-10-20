from abc import ABC, abstractmethod
from uauth.entity.models import UserDetail
from django.contrib.auth.models import User


class UAuthRepository(ABC):
    @abstractmethod
    def create(self, **kwargs):
        pass

    @abstractmethod
    def check_username(self, username):
        pass


class UAuthRepositoryImpl(UAuthRepository):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def create(self, **kwargs):
        user = kwargs['user']
        birthday = kwargs['birthday']
        profile = kwargs['profile']

        return UserDetail.objects.create(
            user=user,
            birthday=birthday,
            profile=profile
        )
    
    def check_username(self, username):
        return User.objects.filter(username=username).exists()