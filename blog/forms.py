from django import forms
from .models import Comment, Blog, Category

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ('title','short_description','category','viewership','publish')


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('comment',)


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ('category',)


class BlogFileAttachmentForm(forms.ModelForm):

    class Meta:
        model = Blog
        fields = ('file_attachment',)

class BlogCoverImageForm(forms.ModelForm):

    class Meta:
        model = Blog
        fields = ('cover_image',)
