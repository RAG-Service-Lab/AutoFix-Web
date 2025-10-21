from django.shortcuts import render, redirect
from django.contrib import auth, messages
from uauth.entity.models import UserForm
from uauth.service.uauth_service import UAuthServiceImpl
from django.http import JsonResponse

uauth_service = UAuthServiceImpl.get_instance()

from django.contrib.auth.views import LoginView

class MyLoginView(LoginView):
    template_name = 'uauth/login.html'

    def form_invalid(self, form):
        print("로그인 실패:", form.errors)  # 터미널에 오류 출력
        return super().form_invalid(form)

def logout(request):
    auth.logout(request)
    return redirect('uauth:login')

def signup(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        print('here1')
        if form.is_valid():
            print('here2')
            user = uauth_service.create(form)
            messages.success(request, '회원가입 완료!')

            # 자동 로그인 처리
            username = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
        else:
            print('form invalid')
            print(form.errors)
            return redirect('uauth:login')
    else:
        print('here3')
        form = UserForm()

    return render(request, 'uauth/signup.html', {'form':form})

def check_username(request):
    username = request.GET.get('username')
    if uauth_service.check_username(username):
        return JsonResponse({'available': False, 'message': '이미 사용중인 ID입니다.'})
    return JsonResponse({'available': True, 'message': '사용 가능한 ID입니다.'})
