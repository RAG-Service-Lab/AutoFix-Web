from abc import ABC, abstractmethod
from uauth.entity.models import UserDetail, Verify
from django.contrib.auth.models import User


class UAuthRepository(ABC):
    @abstractmethod
    def create(self, **kwargs):
        pass

    @abstractmethod
    def check_username(self, username):
        pass

    @abstractmethod
    def get_user_by_email(self, email):
        pass

    @abstractmethod
    def update_password(self, user, new_password):
        pass

    @abstractmethod
    def save_verification_code(self, email, code):
        pass

    @abstractmethod
    def get_verification_code(self, email):
        pass

    @abstractmethod
    def delete_verification_code(self, email):
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
    
    def get_user_by_email(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    def update_password(self, user, new_password):
        user.set_password(new_password)
        user.save(update_fields=['password'])
        return user

    def save_verification_code(self, email, code):
        Verify.objects.update_or_create(email=email, defaults={"code": code})

    def get_verification_code(self, email):
        try:
            return Verify.objects.get(email=email)
        except Verify.DoesNotExist:
            return None

    def delete_verification_code(self, email):
        Verify.objects.filter(email=email).delete()