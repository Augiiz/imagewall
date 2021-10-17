from django.contrib import admin
from .models import Post, Comment, Rating, ReportedPost

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Rating)
admin.site.register(ReportedPost)