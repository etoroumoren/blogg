from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from .models import Post, Comment
from .forms import CommentForm, PostForm

# Create your views here.

def post_list(request):
    published_posts = Post.published.exclude(slug="").order_by('-created')
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

    comments = post.comments.filter(approved=True)

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.approved = False
            comment.save()
            messages.success(request, 'Your comment has been submitted and is awaiting approval.')
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



