from abc import ABC, abstractmethod
from uauth.repository.uauth_repository import UAuthRepositoryImpl
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.core.exceptions import ValidationError


class UAuthService(ABC):
    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def check_username(self, username):
        pass

    @abstractmethod
    def reset_password(self, email, password1, password2):
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
    
    def reset_password(self, email, password1, password2):
        errors = []

        # 1️⃣ 비밀번호 일치 검사
        if password1 != password2:
            errors.append("비밀번호가 일치하지 않습니다.")
            return None, errors

        # 2️⃣ 비밀번호 유효성 검사
        try:
            validate_password(password2)
        except ValidationError as e:
            errors.extend(e.messages)
            return None, errors

        # 3️⃣ 사용자 존재 여부 검사
        user = self.__uauth_repository.get_user_by_email(email)
        if not user:
            errors.append("존재하지 않는 이메일입니다.")
            return None, errors

        # 4️⃣ 비밀번호 변경
        with transaction.atomic():
            user = self.__uauth_repository.update_password(user, password2)

        return user, []