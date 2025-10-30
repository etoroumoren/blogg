from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .models import Post, Comment
from .forms import CommentForm, PostForm

# Create your views here.

def post_list(request):
    posts = Post.published.all()

    return render(
        request,
        'blog/post_list.html',
        {'posts': posts}
    )


def post_detail(request, slug):
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
        return redirect('blog:post_list')

    return render(
        request,
        'blog/post_confirm_delete.html',
        {
            'post': post
        }
    )
