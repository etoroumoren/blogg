from django import forms
from django.utils.text import slugify
from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'slug', 'content', 'status']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }


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
