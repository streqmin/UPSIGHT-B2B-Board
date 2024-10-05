# boards/tests/update/test_update_post.py

import pytest
from rest_framework import status
from django.urls import reverse

# ============================
# 게시글 수정 테스트
# ============================

@pytest.mark.django_db
def test_update_post(authenticated_client, post):
    """
    게시글 수정 테스트 (게시글 소유자)
    """
    url = reverse('post-detail', args=[post.id])
    data = {
        'title': 'Updated Post Title',
        'content': 'Updated content.',
        'is_public': False
    }
    response = authenticated_client.put(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    post.refresh_from_db()
    assert post.title == 'Updated Post Title'
    assert post.is_public == False

@pytest.mark.django_db
def test_update_post_to_public(authenticated_client, draft_post):
    """
    게시글 공개 테스트 (게시글 소유자)
    """
    url = reverse('post-detail', args=[draft_post.id])
    data = {
        'title': draft_post.title,
        'content': draft_post.content,
        'is_public': True
    }
    response = authenticated_client.put(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    draft_post.refresh_from_db()
    assert draft_post.is_public == True

@pytest.mark.django_db
def test_update_users_post_business_admin(admin_authenticated_client, post, admin_user):
    """
    비즈니스 관리자가 다른 사용자의 게시글을 수정할 수 있는지 테스트
    """
    url = reverse('post-detail', args=[post.id])
    data = {
        'title': 'Updated Post Title',
        'content': 'Updated content.',
        'is_public': False
    }
    response = admin_authenticated_client.patch(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    post.refresh_from_db()
    assert post.title == 'Updated Post Title'
    assert post.content == 'Updated content.'
    assert post.is_public == False

@pytest.mark.django_db
def test_update_post_non_owner(non_owner_authenticated_client, post):
    """
    게시글 수정 시도 (비소유자 사용자)
    """
    url = reverse('post-detail', args=[post.id])
    data = {
        'title': 'Hacked Title',
        'content': 'Hacked content.'
    }
    response = non_owner_authenticated_client.put(url, data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN
    post.refresh_from_db()
    assert post.title != 'Hacked Title'

@pytest.mark.django_db
def test_update_post_unauthenticated(api_client, post):
    """
    비인증 사용자가 게시글 수정 시도 시 401 Unauthorized 응답을 받는지 테스트
    """
    url = reverse('post-detail', args=[post.id])
    data = {'is_public': False}
    response = api_client.patch(url, data, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
