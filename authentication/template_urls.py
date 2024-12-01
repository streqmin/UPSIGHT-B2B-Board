from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('login/', views.LoginTemplateView.as_view(), name='login'),  # 로그인 페이지
    path('register/', views.RegisterTemplateView.as_view(), name='register'),  # 회원가입 페이지
]
