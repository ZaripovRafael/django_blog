from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


MAX_POST_ON_LIST = 10


def paginate(
        request,
        query_set,
        post_number=MAX_POST_ON_LIST) -> Paginator:

    paginator = Paginator(query_set, post_number)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    """Функция для рендера главной страницы"""
    post_list = Post.objects.select_related('group').all()
    page_obj = paginate(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Функция для рендера страницы с постами руппы"""
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.all()
    page_obj = paginate(request, posts_list)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):

    user = get_object_or_404(User, username=username)
    posts = user.posts.all()
    posts_count = user.posts.count()
    page_obj = paginate(request, posts)
    context = {
        'author': user,
        'posts_count': posts_count,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    number_of_posts = post.author.posts.count()

    context = {
        'post': post,
        'number_of_post': number_of_posts,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):

    form = PostForm(request.POST or None, files=request.FILES or None)

    if not form.is_valid():
        context = {'form': form}
        return render(request, 'posts/create_post.html', context)

    post = form.save(commit=False)
    post.author = request.user
    post.save()
    username = request.user.username
    return redirect('posts:profile', username=username)


@login_required
def post_edit(request, post_id):

    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if post.author.id == request.user.id:
        if not form.is_valid():
            context = {
                'form': form,
                'is_edit': True,
                'post_id': post_id
            }
            return render(request, 'posts/create_post.html', context)
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:post_detail', post_id=post.pk)
    return redirect('posts:post_detail', post_id=post.pk)
