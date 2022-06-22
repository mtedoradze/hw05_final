from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    # Страница регистрации
    path(
        'signup/',
        views.SignUp.as_view(template_name='users/signup.html'),
        name='signup'
    ),
    # Выход
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    # Страница авторизации
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    # Страница восстановления пароля
    path(
        'password_reset/',
        PasswordResetView.as_view(template_name='users/password_reset.html'),
        name='password_reset'
    ),
    # Сообщение об отправке ссылки для восстановления пароля
    path(
        'password_reset/done/',
        PasswordResetDoneView.as_view(),
        name='password_reset_done'
    ),
    # Вход по ссылке для восстановления пароля
    path(
        'reset/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),
    # Сообщение об успешном восстановлении пароля
    path(
        'reset/done/',
        PasswordResetCompleteView.as_view(),
        name='password_reset_complete'
    )
]
