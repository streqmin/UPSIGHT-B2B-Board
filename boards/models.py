# boards/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser

class Business(models.Model):
    name = models.CharField(max_length=255)
    # 추가 필드가 필요하면 여기에 작성

    def __str__(self):
        return self.name

class BusinessMember(AbstractUser):
    BUSINESS_ADMIN = 'admin'
    BUSINESS_MEMBER = 'member'

    ROLE_CHOICES = [
        (BUSINESS_ADMIN, 'Business Admin'),
        (BUSINESS_MEMBER, 'Business Member'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=BUSINESS_MEMBER)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='members', null=True, blank=True)

    def __str__(self):
        return self.username

class Post(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(BusinessMember, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)
    content = models.TextField()
    is_public = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(BusinessMember, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    is_public = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'