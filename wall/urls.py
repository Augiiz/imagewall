from django.contrib import admin
from django.urls import path, include
from . import views
from .views import PostUpdateView, user_liked_posts, PostListView, UserPostListView, UserPostStatsView, PostListViewByRating, UserPostListViewByRating

urlpatterns=[
	path('', PostListView.as_view(), name='home'),
	path('top/', PostListViewByRating.as_view(), name='home-by-rating'),
	path('post/new/', views.create_post, name='post-create'),
	path('post/<int:pk>/report/', views.ReportPost, name='post-report'),
	path('post/<int:pk>/', views.post_detail, name='post-detail'),
	path('like/', views.like, name='post-like'),
	path('dislike/', views.dislike, name='post-dislike'),
	path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
	path('post/<int:pk>/delete/', views.post_delete, name='post-delete'),
	path('search_posts/', views.search_posts, name='search-posts'),
	path('search_posts_top/', views.search_posts_rating, name='search-posts-rating'),
	path('user_posts/<str:username>', UserPostListView.as_view(), name='user-posts'),
	path('user_posts_top/<str:username>', UserPostListViewByRating.as_view(), name='user-posts-by-rating'),
	path('user_liked_posts/<str:username>', user_liked_posts.as_view(), name='user-liked-posts'),
	path('user_stats/<str:username>', UserPostStatsView.as_view(), name='user-stats'),
	path('category/', views.category, name='category'),
	path('category_top/', views.categoryByRating, name='category-by-rating'),

]