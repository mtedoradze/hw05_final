from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from .models import Post, Group, Follow
from .forms import PostForm, CommentForm
from . import utils


User = get_user_model()


def index(request):
    """Все посты. Применяется паджинатор."""
    post_list = Post.objects.select_related(
        'author',
        'group'
    )
    page_obj = utils.paginate(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Посты группы. Применяется паджинатор."""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author', 'group')
    page_obj = utils.paginate(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Посты автора. Применяется паджинатор."""
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('author', 'group')
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user,
        author=(User.objects.get(username=username))
    ).exists()
    page_obj = utils.paginate(request, post_list)
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Страница поста: вывод подробной информации о посте"""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        comments = add_comment(request, post_id)
    comments = post.comments.select_related('post')
    context = {
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Создание нового поста, после успешного заполнения -
    переход на страницу профиля"""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', request.user)

    return render(request, 'posts/post_create.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """Редактирование поста - доступно только автору поста,
    если пользователь - не автор - переход на страницу поста.
    После успешного редактирования - переход на страницу поста"""
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)

    if request.method == 'POST':
        if form.is_valid():
            post = form.save()
            post.save()
        return redirect('posts:post_detail', post_id)

    return render(request,
                  'posts/post_create.html',
                  {'form': form,
                   'is_edit': True,
                   'post': post
                   }
                  )


@login_required
def add_comment(request, post_id):
    """Добавление комментария к посту -
    доступно только авторизованному пользователю."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    print(form.errors)
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Страница постов авторов, на которых подписан
    пользователь."""
    user = get_object_or_404(User, username=request.user)
    post_list = Post.objects.filter(
        author__following__user=user
    ).select_related('author', 'group')
    page_obj = utils.paginate(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    if User.objects.get(
        username=username
    ) == request.user or Follow.objects.filter(
        user=request.user,
        author=(User.objects.get(username=username))
    ).exists():
        return redirect('posts:profile', request.user)
    Follow.objects.create(
        user=request.user,
        author=(User.objects.get(username=username))
    )
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    unfollow = Follow.objects.filter(
        user=request.user,
        author=(User.objects.get(username=username))
    )
    unfollow.delete()
    return redirect('posts:index')
