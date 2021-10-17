from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

categories = (
('general','General'),
('funny','Funny'),
('serious', 'Serious'),
('animals','Animals'),
('nature','Nature'),
('useful','Useful'),
('infographics','Infographics'),
)


class Post(models.Model):
	title = models.CharField(max_length=255, blank=False)
	image = models.ImageField(upload_to='imgs')
	date_posted = models.DateTimeField(default=timezone.now)
	user_name = models.ForeignKey(User, on_delete=models.CASCADE)
	tags = models.CharField(max_length=100, blank=False)
	category = models.CharField(max_length=100, choices=categories, default="General", blank=False)
	hide_from_guests = models.BooleanField(default=False)
	rating = models.IntegerField(default=0)

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('post-detail', kwargs={'pk': self.pk})

	def split_tags(self):
		tags = self.tags.split()
		return(tags)

	def get_tag_url(self):
		return "/search_posts/?p="

	def get_category_url(self):
		return "/category/?p="

	def hide_post(self):
		return self.hide_from_guests

	def likeCount(self):
		return Rating.objects.filter(post=self.pk, ratingtype='like').count()

	def dislikeCount(self):
		return Rating.objects.filter(post=self.pk, ratingtype='dislike').count()


class Comment(models.Model):
	post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
	username = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
	comment = models.CharField(max_length=255)
	comment_date = models.DateTimeField(default=timezone.now)

class ReportedPost(models.Model):
	post = models.ForeignKey(Post, related_name='reported', on_delete=models.CASCADE)
	user = models.ForeignKey(User, related_name='reported', on_delete=models.CASCADE)
	reason = models.CharField(max_length=255)
	report_date = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return str(self.post)

class Rating(models.Model):
	user = models.ForeignKey(User, related_name='rate', on_delete=models.CASCADE)
	post = models.ForeignKey(Post, related_name='rate', on_delete=models.CASCADE)
	ratingtype = models.CharField(max_length=7, default="None")

