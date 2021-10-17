from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .forms import NewCommentForm, NewPostForm, ReportForm
from django.views.generic import ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post, Comment, Rating, ReportedPost
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import F
import json
import os

class PostListView(ListView):
	model = Post
	template_name = 'home.html'
	context_object_name = 'posts'
	ordering = ['-date_posted']
	paginate_by = 25
	def get_context_data(self, **kwargs):
		context = super(PostListView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated:
			liked = [i for i in Post.objects.all() if Rating.objects.filter(user = self.request.user, post=i, ratingtype='like')]
			disliked = [i for i in Post.objects.all() if Rating.objects.filter(user = self.request.user, post=i, ratingtype='dislike')]
			context['liked_post'] = liked
			context['disliked_post'] = disliked
		return context

class PostListViewByRating(ListView):
	model = Post
	template_name = 'home.html'
	context_object_name = 'posts'
	ordering = ['-rating']
	paginate_by = 25
	def get_context_data(self, **kwargs):
		context = super(PostListViewByRating, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated:
			liked = [i for i in Post.objects.all() if Rating.objects.filter(user = self.request.user, post=i, ratingtype='like')]
			disliked = [i for i in Post.objects.all() if Rating.objects.filter(user = self.request.user, post=i, ratingtype='dislike')]
			context['liked_post'] = liked
			context['disliked_post'] = disliked
		return context

class UserPostListView(LoginRequiredMixin, ListView):
	model = Post
	template_name = 'user_posts.html'
	context_object_name = 'posts'
	paginate_by = 25

	def get_context_data(self, **kwargs):
		context = super(UserPostListView, self).get_context_data(**kwargs)
		user = get_object_or_404(User, username=self.kwargs.get('username'))
		liked = [i for i in Post.objects.filter(user_name=user) if Rating.objects.filter(user = self.request.user, post=i, ratingtype='like')]
		disliked = [i for i in Post.objects.filter(user_name=user) if Rating.objects.filter(user = self.request.user, post=i, ratingtype='dislike')]
		context['liked_post'] = liked
		context['disliked_post'] = disliked
		return context

	def get_queryset(self):
		user = get_object_or_404(User, username=self.kwargs.get('username'))
		return Post.objects.filter(user_name=user).order_by('-date_posted')

class UserPostListViewByRating(LoginRequiredMixin, ListView):
	model = Post
	template_name = 'user_posts.html'
	context_object_name = 'posts'
	paginate_by = 25

	def get_context_data(self, **kwargs):
		context = super(UserPostListViewByRating, self).get_context_data(**kwargs)
		user = get_object_or_404(User, username=self.kwargs.get('username'))
		liked = [i for i in Post.objects.filter(user_name=user) if Rating.objects.filter(user = self.request.user, post=i, ratingtype='like')]
		disliked = [i for i in Post.objects.filter(user_name=user) if Rating.objects.filter(user = self.request.user, post=i, ratingtype='dislike')]
		context['liked_post'] = liked
		context['disliked_post'] = disliked
		return context

	def get_queryset(self):
		user = get_object_or_404(User, username=self.kwargs.get('username'))
		return Post.objects.filter(user_name=user).order_by('-rating')


class UserPostStatsView(LoginRequiredMixin, ListView):
	model = Post
	template_name = 'user_stats.html'
	context_object_name = 'posts'

	def get_queryset(self):
		user = get_object_or_404(User, username=self.kwargs.get('username'))
		return Post.objects.filter(user_name=user).order_by('-rating')


@login_required
def post_detail(request, pk):
	post = get_object_or_404(Post, pk=pk)
	user = request.user
	is_liked =  Rating.objects.filter(user=user, post=post, ratingtype='like')
	is_disliked =  Rating.objects.filter(user=user, post=post, ratingtype='dislike')
	if request.method == 'POST':
		form = NewCommentForm(request.POST)
		if form.is_valid():
			data = form.save(commit=False)
			data.post = post
			data.username = user
			data.save()
			return redirect('post-detail', pk=pk)
	else:
		form = NewCommentForm()
	return render(request, 'post_detail.html', {'post':post, 'is_liked':is_liked, 'is_disliked':is_disliked, 'form':form})

@login_required
def create_post(request):
	user = request.user
	if request.method == "POST":
		form = NewPostForm(request.POST, request.FILES)
		if form.is_valid():
			data = form.save(commit=False)
			data.user_name = user
			data.save()
			messages.success(request, f'Posted Successfully')
			return redirect('home')
	else:
		form = NewPostForm()
	return render(request, 'create_post.html', {'form':form})

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = Post
	fields = ['title', 'tags', 'hide_from_guests']
	template_name = 'create_post.html'

	def form_valid(self, form):
		form.instance.user_name = self.request.user
		return super().form_valid(form)

	def test_func(self):
		post = self.get_object()
		if self.request.user == post.user_name or self.request.user.is_superuser:
			return True
		return False


@login_required
def ReportPost(request, pk):
	post = get_object_or_404(Post, pk=pk)
	user = request.user
	if request.method == 'POST':
		form = ReportForm(request.POST)
		if ReportedPost.objects.filter(user=user, post=post):
			messages.info(request, 'You have already reported this post before!')
			return redirect('post-detail', pk=pk)
		else:
			if form.is_valid():
				data = form.save(commit=False)
				data.post = post
				data.user = user
				data.save()
				messages.info(request, 'Post has been reported.')
				return redirect('post-detail', pk=pk)
	else:
		form = ReportForm()
	return render(request, 'create_post.html', {'form':form})

@login_required
def post_delete(request, pk):
	post = Post.objects.get(pk=pk)
	img = str(post.image)
	if os.path.isfile('media/' + img):
		os.remove('media/' + img)
	if request.user == post.user_name or request.user.is_superuser:
		Post.objects.get(pk=pk).delete()
	return redirect('home')

class user_liked_posts(LoginRequiredMixin, ListView):
	model = Post
	template_name = 'user_posts.html'
	context_object_name = 'posts'
	paginate_by = 25

	def get_context_data(self, **kwargs):
		context = super(user_liked_posts, self).get_context_data(**kwargs)
		user = get_object_or_404(User, username=self.kwargs.get('username'))
		liked = [i for i in Post.objects.all() if Rating.objects.filter(user = self.request.user, post=i, ratingtype='like')]
		context['liked_post'] = liked
		return context

	def get_queryset(self):
		user = get_object_or_404(User, username=self.kwargs.get('username'))
		if self.request.user == user or self.request.user.is_superuser:
			return Post.objects.filter(rate__ratingtype='like', rate__user_id=user)
		else:
			return


@login_required
def search_posts(request):
	query = request.GET.get('p')
	object_list = Post.objects.filter(tags__icontains=query).order_by('-date_posted')
	liked = [i for i in object_list if Rating.objects.filter(user = request.user, post=i, ratingtype='like')]
	disliked = [i for i in object_list if Rating.objects.filter(user = request.user, post=i, ratingtype='dislike')]
	context ={
		'posts': object_list,
		'liked_post': liked,
		'disliked_post': disliked
	}
	return render(request, "search_posts.html", context)


@login_required
def search_posts_rating(request):
	query = request.GET.get('p')
	object_list = Post.objects.filter(tags__icontains=query).order_by('-rating')
	liked = [i for i in object_list if Rating.objects.filter(user = request.user, post=i, ratingtype='like')]
	disliked = [i for i in object_list if Rating.objects.filter(user = request.user, post=i, ratingtype='dislike')]
	context ={
		'posts': object_list,
		'liked_post': liked,
		'disliked_post': disliked
	}
	return render(request, "search_posts.html", context)



@login_required
def category(request):
	query = request.GET.get('p')
	object_list = Post.objects.filter(category__icontains=query).order_by('-date_posted')
	liked = [i for i in object_list if Rating.objects.filter(user = request.user, post=i, ratingtype='like')]
	disliked = [i for i in object_list if Rating.objects.filter(user = request.user, post=i, ratingtype='dislike')]
	context ={
		'posts': object_list,
		'liked_post': liked,
		'disliked_post': disliked
	}

	return render(request, "search_posts.html", context)

@login_required
def categoryByRating(request):
	query = request.GET.get('p')
	object_list = Post.objects.filter(category__icontains=query).order_by('-rating')
	liked = [i for i in object_list if Rating.objects.filter(user = request.user, post=i, ratingtype='like')]
	disliked = [i for i in object_list if Rating.objects.filter(user = request.user, post=i, ratingtype='dislike')]
	context ={
		'posts': object_list,
		'liked_post': liked,
		'disliked_post': disliked
	}
	return render(request, "search_posts.html", context)

@login_required
def like(request):
	post_id = request.GET.get("likeId", "")
	user = request.user
	post = Post.objects.get(pk=post_id)
	liked= False
	like = Rating.objects.filter(user=user, post=post, ratingtype='like')
	if like:
		like.delete()
		Post.objects.filter(pk=post_id).update(rating=F('rating')-1)
	else:
		liked = True
		if Rating.objects.filter(user=user, post=post, ratingtype='dislike'):
			Rating.objects.filter(user=user, post=post, ratingtype='dislike').update(ratingtype='like')
			Post.objects.filter(pk=post_id).update(rating=F('rating')+2)
		else:
			Rating.objects.create(user=user, post=post, ratingtype='like')
			Post.objects.filter(pk=post_id).update(rating=F('rating')+1)
	resp = {
        'liked':liked
    }
	response = json.dumps(resp)
	return HttpResponse(response, content_type = "application/json")

@login_required
def dislike(request):
	post_id = request.GET.get("dislikeId", "")
	user = request.user
	post = Post.objects.get(pk=post_id)
	disliked= False
	dislike = Rating.objects.filter(user=user, post=post, ratingtype='dislike')
	if dislike:
		dislike.delete()
		Post.objects.filter(pk=post_id).update(rating=F('rating')+1)
	else:
		disliked = True
		if Rating.objects.filter(user=user, post=post, ratingtype='like'):
			Rating.objects.filter(user=user, post=post, ratingtype='like').update(ratingtype='dislike')
			Post.objects.filter(pk=post_id).update(rating=F('rating')-2)
		else:
			Rating.objects.create(user=user, post=post, ratingtype='dislike')
			Post.objects.filter(pk=post_id).update(rating=F('rating')-1)
	resp = {
        'disliked':disliked
    }
	response = json.dumps(resp)
	return HttpResponse(response, content_type = "application/json")
