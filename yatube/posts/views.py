from django.core.paginator import Paginator
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Follow, Post, Group, User

POSTS_AMOUNT = 10


@cache_page(20, key_prefix='index_page')
def index(request):
    template = 'posts/index.html'
    posts = Post.objects.select_related('group')
    paginator = Paginator(posts, POSTS_AMOUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    description = 'Последние обновления на сайте'

    context = {
        'description': description,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all().order_by('-created').select_related(
        'author'
    )
    paginator = Paginator(posts, POSTS_AMOUNT)
    page_num = request.GET.get('page')
    page_obj = paginator.get_page(page_num)

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    comments = list(post.comments.all())
    comments_form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'comments_form': comments_form,
    }

    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    user = request.user
    author = get_object_or_404(User, username=username)
    following = user.is_authenticated and Follow.objects.filter(
        user=user, author=author
    ).exists()
    posts = author.posts.all().select_related('group')
    posts_num = posts.count()
    paginator = Paginator(posts, POSTS_AMOUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    description = f'Профайл пользователя {username}'

    context = {
        'description': description,
        'author': author,
        'posts_num': posts_num,
        'page_obj': page_obj,
        'following': following,
    }

    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect('posts:profile', request.user.username)
    context = {
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        edited_post = form.save(commit=False)
        edited_post.author = request.user
        edited_post.save()
        return redirect('posts:post_detail', post_id)
    is_edit = True
    context = {
        'form': form,
        'is_edit': is_edit,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments_form = CommentForm(request.POST or None)
    if comments_form.is_valid():
        comments_form.instance.author = request.user
        comments_form.instance.post = post
        comments_form.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    user = request.user
    followings = Follow.objects.filter(user=user)
    message = ''
    if not followings:
        message = (
            'Подпишитесь на кого-нибудь, '
            'чтобы следить за их обновлениями'
        )
    posts = Post.objects.filter(
        author__following__user=user
    )
    paginator = Paginator(posts, POSTS_AMOUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    description = 'Последние обновления у избранных авторов'
    context = {
        'description': description,
        'page_obj': page_obj,
        'message': message,
    }
    return render(request, 'posts/index.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if user != author:
        Follow.objects.get_or_create(
            user=user,
            author=author
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(user=user, author=author).exists()
    if following:
        Follow.objects.filter(user=user, author=author).delete()
    return redirect('posts:profile', username=username)
