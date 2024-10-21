# boards/serializers.py

from rest_framework import serializers
from .models import Post, Comment

class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    business = serializers.ReadOnlyField(source='business.id')  # Business는 현재 사용자와 연관됨

    class Meta:
        model = Post
        fields = ['id', 'business', 'author', 'title', 'content', 'is_public', 'deleted_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'business', 'author', 'created_at', 'updated_at']

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'is_public', 'deleted_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'post', 'author', 'created_at', 'updated_at']
