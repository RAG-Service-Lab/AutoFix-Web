import json
from django.shortcuts import render, redirect
from django.contrib import auth, messages
from uauth.entity.models import UserForm
from uauth.service.uauth_service import UAuthServiceImpl
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from uauth.entity.models import UserForm
from rest_framework.exceptions import ValidationError
from django.contrib.auth.decorators import login_required

uauth_service = UAuthServiceImpl.get_instance()

from django.contrib.auth.views import LoginView

class MyLoginView(LoginView):
    template_name = 'uauth/login.html'

    def form_invalid(self, form):
        print("로그인 실패:", form.errors)  # 터미널에 오류 출력
        return super().form_invalid(form)

class SendVerificationCodeView(APIView):
    def post(self, request):
        email = request.data.get("email")
        purpose = request.data.get("purpose", "signup")

        if not email:
            return Response({"message": "이메일을 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        signup = True if purpose == "signup" else False
        service = UAuthServiceImpl.get_instance()
        try:
            service.send_verification_email(email, signup =signup )
            return Response({"message": "인증 코드가 이메일로 전송되었습니다."}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class VerifyCodeView(APIView):
    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")

        service = UAuthServiceImpl.get_instance()
        try:
            service.verify_code(email, code)
            return Response({"message": "인증이 완료되었습니다."}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserRegisterView(APIView):
    def post(self, request):
        form = UserForm(data=request.data)  # ✅ data=로 전달
        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

        service = UAuthServiceImpl.get_instance()
        email = form.cleaned_data.get('email')
        code = request.data.get('verification_code')  # 클라이언트에서 받은 인증코드

        # 이메일 인증 여부 검증
        if not service.verify_code(email, code):  # ✅ Service에 verify_code 메서드 필요
            return Response({"message": "이메일 인증을 완료해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        # 회원 생성
        user = service.create(form)
        return Response({"message": "회원가입이 완료되었습니다."}, status=status.HTTP_201_CREATED)

class DeleteAccountView(APIView):
    """
    회원탈퇴 API
    POST로 { password } 보내면 현재 로그인된 사용자의 이메일 기반 탈퇴
    """
    def post(self, request):
        email = request.user.email if request.user.is_authenticated else None
        password = request.data.get("password")

        if not email:
            return Response({"message": "로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED)
        if not password:
            return Response({"message": "비밀번호를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        service = UAuthServiceImpl.get_instance()
        try:
            service.delete_account(email, password)
            # 로그아웃 처리
            from django.contrib import auth
            auth.logout(request)
            return Response({"message": "회원탈퇴가 완료되었습니다."}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def logout(request):
    auth.logout(request)
    return redirect('uauth:login')

def signup(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            user = uauth_service.create(form)
            username = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
        else:
            print('form invalid')
            print(form.errors)
            return redirect('uauth:login')
    else:
        form = UserForm()

    return render(request, 'uauth/signup.html', {'form':form})

def signout(request):

    return render(request, 'uauth/signout.html')

def reset_password(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password1 = data.get('password1')
            password2 = data.get('password2')
        except:
            return JsonResponse({'message': '잘못된 요청입니다.'}, status=400)

        user, errors = uauth_service.reset_password(email, password1, password2)
        if errors:
            return JsonResponse({'message': errors[0]}, status=400)
        return JsonResponse({'message': '비밀번호가 성공적으로 변경되었습니다.'})
    
    # GET 요청 시
    return render(request, 'uauth/reset_password.html')


def check_username(request):
    username = request.GET.get('username')
    if uauth_service.check_username(username):
        return JsonResponse({'available': False, 'message': '이미 사용중인 ID입니다.'})
    return JsonResponse({'available': True, 'message': '사용 가능한 ID입니다.'})

