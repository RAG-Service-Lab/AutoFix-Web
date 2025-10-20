from abc import ABC, abstractmethod
from uauth.repository.uauth_repository import UAuthRepositoryImpl
from django.db import transaction


class UAuthService(ABC):
    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def check_username(self, username):
        pass


class UAuthServiceImpl(UAuthService):
    __instance = None
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        self.__uauth_repository = UAuthRepositoryImpl.get_instance()

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    # @transaction.atomic
    def create(self, form):
        with transaction.atomic():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()

            userdetail = self.__uauth_repository.create(
                user=user,
                birthday=form.cleaned_data.get('birthday'),
                profile=form.cleaned_data.get('profile')
            )
        return user

    def check_username(self, username):
        return self.__uauth_repository.check_username(username)
    