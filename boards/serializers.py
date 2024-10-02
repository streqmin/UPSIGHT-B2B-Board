# boards/serializers.py

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from .models import BusinessMember, Business, Post, Comment

class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=BusinessMember.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}
    )
    business = serializers.PrimaryKeyRelatedField(queryset=Business.objects.all())

    class Meta:
        model = BusinessMember
        fields = ('username', 'password', 'password2', 'business', 'role')
        extra_kwargs = {
            # 'first_name': {'required': False},
            # 'last_name': {'required': False},
            'role': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        if attrs['role'] not in ['admin', 'member']:
            raise serializers.ValidationError({"role": "Role must be either 'admin' or 'member'."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = BusinessMember.objects.create(
            username=validated_data['username'],
            # first_name=validated_data['first_name'],
            # last_name=validated_data['last_name'],
            business=validated_data['business'],
            role=validated_data['role']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    business = serializers.ReadOnlyField(source='business.id')  # Business는 현재 사용자와 연관됨

    class Meta:
        model = Post
        fields = ['id', 'business', 'author', 'title', 'content', 'is_public', 'is_deleted', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'is_public', 'is_deleted', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']
