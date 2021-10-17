from django import forms
from .models import Comment, Post, ReportedPost

class NewPostForm(forms.ModelForm):
	class Meta:
		model = Post
		fields = ['title', 'image', 'category', 'tags', 'hide_from_guests']

class NewCommentForm(forms.ModelForm):
	class Meta:
		model = Comment
		fields = ['comment']

class ReportForm(forms.ModelForm):
	class Meta:
		model = ReportedPost
		fields = ['reason']