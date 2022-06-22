from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    # Главная страница
    path('', views.index, name='index'),
    # Профайл пользователя
    path('profile/<str:username>/', views.profile, name='profile'),
    # Просмотр поста
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    # Новый пост
    path('create/', views.post_create, name='post_create'),
    # Редактирование поста
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    # Страница группы
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    # Добавление комментария к посту
    path(
        'posts/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment'
    ),
    # Страница постов автора, на которых подписан пользователь
    path('follow/', views.follow_index, name='follow_index'),
    # Подписка на автора
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    # Отписка от автора
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
]
