# boards/tests/delete/test_delete_post.py

import pytest
from rest_framework import status
from django.urls import reverse

# ============================
# 게시글 삭제 테스트
# ============================

@pytest.mark.django_db
def test_delete_post(authenticated_client, post):
    """
    게시글 삭제 테스트 (게시글 소유자)
    """
    url = reverse('post-detail', args=[post.id])
    response = authenticated_client.delete(url, format='json')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    post.refresh_from_db()
    assert post.deleted_at 

@pytest.mark.django_db
def test_delete_post_non_owner(non_owner_authenticated_client, post):
    """
    게시글 삭제 시도 (비소유자 사용자)
    """
    url = reverse('post-detail', args=[post.pk])
    response = non_owner_authenticated_client.delete(url, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN
    post.refresh_from_db()
    assert post.deleted_at is None

@pytest.mark.django_db
def test_delete_post_unauthenticated(api_client, post):
    """
    비인증 사용자가 게시글 삭제 시도 시 401 Unauthorized 응답을 받는지 테스트
    """
    url = reverse('post-detail', args=[post.id])
    response = api_client.delete(url, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
