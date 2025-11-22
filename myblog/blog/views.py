from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.postgres.search import SearchVector
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
import markdown
from django.utils.safestring import mark_safe
from .models import Comment, Post, Profile
from taggit.models import Tag
from .forms import (
    CommentForm,
    LoginForm,
    PostForm,
    UserRegistrationForm,
    UserEditForm,
    ProfileEditForm,
    SearchForm,
)
from django.http import HttpResponse

# Create your views here.


@login_required
def account(request):
    return render(
        request,
        'blog/account.html',
        {
            'section': 'account'
        }
    )

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(
                user_form.cleaned_data['password']
            )
            new_user.save()
            Profile.objects.get_or_create(user=new_user)
            return render(
                request,
                'blog/register_done.html',
                {
                    'new_user': new_user
                }
            )
    else:
        user_form = UserRegistrationForm()
    return render(
        request,
        'blog/register.html',
        {
            'user_form': user_form
        }
    )


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(
            instance=request.user,
            data=request.POST
        )
        profile_form = ProfileEditForm(
            instance=request.user.profile,
            data=request.POST,
            files=request.FILES
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(
        request,
        'blog/edit.html',
        {
            'user_form': user_form,
            'profile_form': profile_form
        }
    )

def post_list(request, tag_slug=None):
    published_posts = Post.published.exclude(slug="").order_by('-created')

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        published_posts = published_posts.filter(tags__in=[tag])

    paginator = Paginator(published_posts, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    user_drafts = []
    if request.user.is_authenticated:
        user_drafts = Post.objects.filter(author=request.user, status='draft')

    return render(
        request,
        'blog/post_list.html',
        {
            'posts': posts,
            'drafts': user_drafts,
            'tag': tag
        }
    )


def post_detail(request, slug):
    if request.user.is_authenticated:
        post = get_object_or_404(
            Post,
            Q(status='published') | Q(author=request.user),
            slug=slug
        )
    else:
        post = get_object_or_404(Post.published, slug=slug)

    post.content_html = mark_safe(markdown.markdown(
        post.content,
        extensions=['fenced_code', 'codehilite', 'tables', 'nl2br']
    ))

    comments = post.comments.filter(approved=True)

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.approved = True
            comment.save()
            messages.success(request, 'Your comment has been posted.')
            return redirect(post.get_absolute_url())
    else:
        comment_form = CommentForm()

    return render(
        request,
        'blog/post_detail.html',
        {
            'comments': comments,
            'comment_form': comment_form,
            'post': post,
        }
    )


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()

            if post.status == 'published':
                messages.success(request, f'Post "{post.title}" published successfully!')
            else:
                messages.success(request, f'Draft "{post.title}" saved successfully!')

            return redirect(post.get_absolute_url())

    else:
        form = PostForm()
    return render(
        request,
        'blog/post_form.html',
        {
            'form': form,
        }
    )


@login_required
def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug)

    if post.author != request.user:
        return redirect(post.get_absolute_url())

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()

            if post.status == 'published':
                messages.success(request, f'Post "{post.title}" published successfully!')
            else:
                messages.success(request, f'Draft "{post.title}" updated successfully!')
            return redirect(post.get_absolute_url())
    else:
        form = PostForm(instance=post)

    return render(
        request,
        'blog/post_form.html',
        {
            'form': form,
            'post': post
        }
    )


@login_required
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug)

    if post.author != request.user:
        return redirect('blog:post_list')


    if request.method == 'POST':
        post.delete()
        messages.success(request, f'Post "{post.title}" deleted successfully!')
        return redirect('blog:post_list')

    return render(
        request,
        'blog/post_confirm_delete.html',
        {
            'post': post
        }
    )

def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = (
                Post.published.annotate(
                    search=SearchVector('title', 'content'),
                )
                .filter(search=query)
            )

    return render(
        request,
        'blog/search.html',
        {
            'form': form,
            'query': query,
            'results': results,
        }
    )
