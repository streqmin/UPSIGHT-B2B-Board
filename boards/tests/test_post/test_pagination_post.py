# boards/tests/read/test_read_post.py

import pytest
from rest_framework import status
from django.urls import reverse
from boards.tests.factories import PostFactory

# ============================
# 페이지네이션 테스트
# ============================

@pytest.mark.django_db
def test_pagination_posts(authenticated_client, user):
    """
    게시글 페이지네이션 테스트
    """
    for _ in range(60):
        PostFactory(author=user, business=user.business)
    url = reverse('post-list') + '?page=1&limit=20'  # 페이지네이션 파라미터에 맞게 수정
    response = authenticated_client.get(url, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 20
    assert 'next' in response.data
    assert 'previous' in response.data

@pytest.mark.django_db
def test_pagination_over_limit(authenticated_client, user):
    """
    존재하지 않는 페이지 번호를 요청했을 때 404 Not Found 응답을 받는지 테스트
    """
    for _ in range(30):
        PostFactory(author=user, business=user.business)
    url = reverse('post-list') + '?page=100&limit=20'  # 존재하지 않는 페이지
    response = authenticated_client.get(url, format='json')
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
def test_pagination_last_page(authenticated_client, user):
    """
    페이지네이션의 마지막 페이지에서 예상한 게시글 수과 next, previous 링크의 상태를 검증
    """
    for _ in range(25):
        PostFactory(author=user, business=user.business)
    url = reverse('post-list') + '?page=2&limit=20'  # 총 25개 게시글, 페이지 2는 5개
    response = authenticated_client.get(url, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 5
    assert response.data['next'] is None
    assert response.data['previous'] is not None
