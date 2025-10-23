from django.contrib.auth import views as auth_views
from django.urls import path
from uauth.controller import views
from uauth.controller.views import MyLoginView, SendVerificationCodeView, VerifyCodeView, UserRegisterView, DeleteAccountView

app_name = 'uauth'

urlpatterns = [
    # path('login/', auth_views.LoginView.as_view(template_name='uauth/login.html'), name='login'),
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('signout/', views.signout, name='signout'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('check_username/', views.check_username, name='check_username'),
    path('send-code/', SendVerificationCodeView.as_view(), name='send_code'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify_code'),
    path('register/', UserRegisterView.as_view(), name='user_register'),
    path('delete_account/', DeleteAccountView.as_view(), name='delete_account'),
]