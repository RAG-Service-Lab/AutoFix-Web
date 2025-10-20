from django.shortcuts import render, redirect
from django.contrib import auth, messages
from uauth.entity.models import UserForm
from uauth.service.uauth_service import UAuthServiceImpl
from django.http import JsonResponse

uauth_service = UAuthServiceImpl.get_instance()

def logout(request):
    auth.logout(request)
    return redirect('index')

def signup(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            user = uauth_service.create(form)
            messages.success(request, '회원가입 완료!')

            # 자동 로그인 처리
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)

            return redirect('index')
    else:
        form = UserForm()

    return render(request, 'uauth/signup.html', {'form':form})


def check_username(request):
    username = request.GET.get('username')
    if uauth_service.check_username(username):
        return JsonResponse({'available': False, 'message': '이미 사용중인 ID입니다.'})
    return JsonResponse({'available': True, 'message': '사용 가능한 ID입니다.'})
