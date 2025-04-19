from django import forms
from django.contrib.auth import get_user_model
from .models import Post, Comment
User = get_user_model()


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = (
            'title',
            'text',
            'category',
            'is_published',
            'image',
            'pub_date',
            'location',
        )
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'date'})
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea()
        }


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
        )
