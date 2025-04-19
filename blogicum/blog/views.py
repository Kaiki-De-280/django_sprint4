from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count

from blog.models import Category, Post, Comment
from blog.forms import UserForm, CommentForm, PostForm
User = get_user_model()


def index(request):
    template = "blog/index.html"
    post_list = Post.objects.filter(
        pub_date__lte=datetime.now(),
        is_published__exact=True,
        category__is_published__exact=True,
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, }
    return render(request, template, context)


def post_detail(request, id):
    """Страница отдельной публикации."""
    template = "blog/detail.html"
    post = get_object_or_404(
        Post,
        # pub_date__lte=datetime.now(),
        # is_published=True,
        # category__is_published=True,
        pk=id,
    )
    if request.user != post.author and post.is_published is False:
        return render(request, 'pages/404.html', status=404)
    comments = Comment.objects.filter(
        post__exact=id,
    ).order_by('created_at')

    form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, template, context)


def category_posts(request, category_slug):
    template = "blog/category.html"
    category = get_object_or_404(
        Category,
        slug__exact=category_slug,
        is_published__exact=True,
    )
    post_list = Post.objects.filter(pub_date__lte=datetime.now(),
                                    category=category,
                                    is_published=True,).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'category': category,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):

    post = get_object_or_404(Post, pk=post_id,)

    if post is None:
        return render(request, 'pages/404.html',)

    form = CommentForm(request.POST or None)

    context = {
        'form': form,
    }

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post_id = post_id
        comment.save()
        return redirect('blog:post_detail', post_id,)

    return render(request, 'blog/comment.html', context,)


@login_required
def edit_comment(request, post_id, comment_id):

    instance = get_object_or_404(Comment, pk=comment_id,)

    if instance.author != request.user:
        return render(request, 'pages/404.html')

    form = CommentForm(
        request.POST or None,
        instance=instance,
    )

    context = {
        'form': form,
        'comment': instance,
    }

    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id,)

    return render(request, 'blog/comment.html', context,)


@login_required
def delete_comment(request, post_id, comment_id):

    instance = get_object_or_404(Comment, pk=comment_id,)

    if not request.user == instance.author:
        return render(request, 'pages/404.html',)

    context = {
        'comment': instance,
    }

    if request.method == 'POST':
        instance.delete()
        return redirect('blog:post_detail', post_id,)

    return render(request, 'blog/comment.html', context)


def create_post(request):

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )

    if form.is_valid() and request.user.is_authenticated:
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', request.user.username)

    context = {
        'form': form,
    }

    return render(request, 'blog/create.html', context=context)


@login_required
def delete_post(request, post_id):

    instance = get_object_or_404(Post, pk=post_id,)

    if request.user != instance.author:
        return render(request, 'pages/404.html',)

    form = PostForm(
        request.POST or None,
        instance=instance,
    )

    context = {
        'form': form,
    }

    if request.method == 'POST':
        instance.delete()
        return redirect('blog:index',)

    return render(request, 'blog/create.html', context=context,)


@login_required
def edit_post(request, post_id):

    instance = get_object_or_404(Post, pk=post_id,)

    if request.user != instance.author:
        return redirect('blog:post_detail', post_id,)

    form = PostForm(
        request.POST or None,
        instance=instance,
        files=request.FILES or None,
    )

    context = {
        'form': form
    }

    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id,)

    return render(request, 'blog/create.html', context=context,)


def profile(request, username):

    user = get_object_or_404(User, username=username)

    if request.user == user:
        posts = Post.objects.filter(
            author_id__exact=user.pk,
        ).order_by('-pub_date').annotate(
            comment_count=Count('comments')
        )
    else:
        posts = Post.objects.filter(
            author_id__exact=user.pk,
            is_published__exact=True,
            category__is_published__exact=True,
        ).order_by('-pub_date').annotate(
            comment_count=Count('comments')
        )

    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    context = {
        'profile': user,
        'page_obj': page_obj,
    }

    return render(request, 'blog/profile.html', context,)


def edit_profile(request):

    instance = get_object_or_404(User, pk=request.user.id,)

    form = UserForm(
        request.POST or None,
        instance=instance,
        files=request.FILES or None,
    )

    context = {
        'form': form
    }

    if form.is_valid():
        form.save()

    return render(request, 'blog/user.html', context,)
