from django import forms
from django.utils.text import slugify
from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'status']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }

    def save(self, commit=True):
        post = super().save(commit=False)

        if not post.slug:
            base_slug = slugify(post.title)
            slug = base_slug
            counter = 1

            while Post.objects.filter(slug=slug).exclude(pk=post.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            post.slug = slug

        if commit:
            post.save()

        return post


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Your comment...'}),
        }
        labels = {
            'content': 'Your Comment',
        }
