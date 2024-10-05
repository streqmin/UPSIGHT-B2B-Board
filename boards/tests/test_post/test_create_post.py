# boards/tests/create/test_create_post.py

import pytest
from rest_framework import status
from django.urls import reverse
from boards.models import Post

# ============================
# 게시글 생성 테스트
# ============================

@pytest.mark.django_db
def test_create_post(authenticated_client, user):
    """
    게시글 생성 테스트 (일반 사용자)
    """
    url = reverse('post-list')
    data = {
        'business': user.business.id,
        'title': 'Test Post',
        'content': 'This is a test post.',
        'is_public': True
    }
    response = authenticated_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    post = Post.objects.get(title='Test Post')
    assert post.author == user
    assert post.business == user.business

@pytest.mark.django_db
def test_create_post_business_admin(admin_authenticated_client, admin_user):
    """
    비즈니스 관리자가 게시글 생성 테스트
    """
    url = reverse('post-list')
    data = {
        'business': admin_user.business.id,
        'title': 'Admin Post',
        'content': 'Post created by admin.',
        'is_public': False
    }
    response = admin_authenticated_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    post = Post.objects.get(title='Admin Post')
    assert post.author == admin_user
    assert post.business == admin_user.business

@pytest.mark.django_db
def test_create_post_unauthenticated(api_client, business):
    """
    비인증 사용자가 게시글 생성 시도 시 401 Unauthorized 응답을 받는지 테스트
    """
    url = reverse('post-list')
    data = {
        'business': business.id,
        'title': 'Unauthorized Post',
        'content': 'This should not be created.',
        'is_public': True
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
