from django.contrib.auth import get_user_model
from django import forms
from django.utils.text import slugify
from .models import Comment, Post, Profile


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


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label='Repeat password',
        widget=forms.PasswordInput
    )

    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name', 'email']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("Passwords don't match.")
        return cd['password2']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email']


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['date_of_birth', 'photo']
