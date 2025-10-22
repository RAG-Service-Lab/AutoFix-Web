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

def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        errors = []

        if password1 != password2:
            errors.append("비밀번호가 일치하지 않습니다.")
        else:
            try:
                validate_password(password2)
            except ValidationError as e:
                errors.extend(e.messages)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            errors.append("존재하지 않는 이메일입니다.")

        if errors:
            return render(request, 'uauth/password_reset.html', {'errors': errors, 'email': email})
        
        # ✅ 비밀번호 변경
        user.set_password(password2)
        user.save()
        return redirect('uauth:login')  # 완료 후 로그인 페이지

    return render(request, 'uauth/password_reset.html')


def check_username(request):
    username = request.GET.get('username')
    if uauth_service.check_username(username):
        return JsonResponse({'available': False, 'message': '이미 사용중인 ID입니다.'})
    return JsonResponse({'available': True, 'message': '사용 가능한 ID입니다.'})

