from abc import ABC, abstractmethod
from uauth.repository.uauth_repository import UAuthRepositoryImpl
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404


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

    @abstractmethod
    def send_verification_email(self, email):
        pass

    @abstractmethod
    def verify_code(self, email, code):
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

    def send_verification_email(self, email, signup=True):

        user_exists = self.__uauth_repository.get_user_by_email(email)

        if signup:
            if user_exists:
                raise ValidationError("이미 가입된 이메일입니다.")
        else:
            if not user_exists:
                raise ValidationError("등록되지 않은 이메일입니다.")

        # 인증코드 생성
        code = get_random_string(length=6)

        # 이메일 발송
        email_message = EmailMessage(
            subject='[서비스명] 이메일 인증코드',
            body=f"인증코드는 {code} 입니다.",
            to=[email],
        )
        email_message.send()

        # DB 저장
        self.__uauth_repository.save_verification_code(email, code)

        return code  # (테스트 용도로 반환, 실제 운영에서는 제외)

    def verify_code(self, email, code):
        verify = self.__uauth_repository.get_verification_code(email)
        if not verify:
            raise ValidationError("인증 정보가 존재하지 않습니다.")
        if verify.code != code:
            raise ValidationError("잘못된 인증 코드입니다.")

        # 성공 시 코드 삭제
        self.__uauth_repository.delete_verification_code(email)
        return True

    def delete_account(self, email, password):
        """
        이메일 + 비밀번호 확인 후 사용자 계정 삭제
        """
        # 1️⃣ 사용자 존재 여부
        user = self.__uauth_repository.get_user_by_email(email)
        if not user:
            raise ValidationError("존재하지 않는 사용자입니다.")

        # 2️⃣ 비밀번호 확인
        if not user.check_password(password):
            raise ValidationError("비밀번호가 일치하지 않습니다.")

        # 3️⃣ 탈퇴 처리 (DB 트랜잭션)
        with transaction.atomic():
            user.delete()
            # 필요시 UserDetail도 CASCADE로 삭제되거나 직접 삭제 가능
            # UserDetail.objects.filter(user=user).delete()

        return True