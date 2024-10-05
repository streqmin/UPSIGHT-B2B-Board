# boards/tests/read/test_read_post.py

import pytest
from rest_framework import status
from django.urls import reverse
from boards.tests.factories import PostFactory
from datetime import datetime
from django.utils import timezone

# ============================
# 게시글 조회 테스트
# ============================

@pytest.mark.django_db
def test_list_posts(authenticated_client, post):
    """
    게시글 목록 조회 테스트 (일반 사용자)
    """
    url = reverse('post-list')
    response = authenticated_client.get(url, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert any(p['id'] == post.id for p in response.data['results'])

@pytest.mark.django_db
def test_retrieve_post(authenticated_client, post):
    """
    특정 게시글 조회 테스트 (일반 사용자)
    """
    url = reverse('post-detail', args=[post.id])
    response = authenticated_client.get(url, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == post.title

@pytest.mark.django_db
def test_retrieve_deleted_post_business_admin(admin_authenticated_client, deleted_post):
    """
    is_deleted=True인 게시글을 비즈니스 관리자가 개별 조회 시 접근이 가능한지 테스트
    """
    url = reverse('post-detail', args=[deleted_post.id])
    response = admin_authenticated_client.get(url, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['is_deleted'] == True

@pytest.mark.django_db
def test_retrieve_deleted_post(authenticated_client, deleted_post):
    """
    is_deleted=True인 게시글을 개별 조회 시 접근이 제한되는지 테스트
    """
    url = reverse('post-detail', args=[deleted_post.id])
    response = authenticated_client.get(url, format='json')
    assert response.status_code == status.HTTP_404_NOT_FOUND

# ============================
# 필터링 및 정렬 테스트 (추가 가능)
# ============================

@pytest.mark.django_db
def test_filter_posts_by_is_public(authenticated_client, published_post, draft_post):
    """
    is_public 필터링 테스트: 공개된 게시글만 조회
    """
    url = reverse('post-list') + '?is_public=True'
    response = authenticated_client.get(url, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert any(p['id'] == published_post.id for p in response.data['results'])
    assert not any(p['id'] == draft_post.id for p in response.data['results'])

@pytest.mark.django_db
def test_order_posts_by_created_at_desc(authenticated_client, user):
    """
    작성일 기준 내림차순 정렬 테스트
    """
    post1 = PostFactory(
        author=user,
        business=user.business,
        title='First Post',
        created_at=timezone.make_aware(datetime(2023, 1, 1, 0, 0, 0))
    )
    post2 = PostFactory(
        author=user,
        business=user.business,
        title='Second Post',
        created_at=timezone.make_aware(datetime(2023, 2, 1, 0, 0, 0))
    )
    url = reverse('post-list') + '?ordering=-created_at'
    response = authenticated_client.get(url, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['results'][0]['id'] == post2.id
    assert response.data['results'][1]['id'] == post1.id

@pytest.mark.django_db
def test_order_posts_by_created_at_aesc(authenticated_client, user):
    """
    작성일 기준 오름차순 정렬 테스트
    """
    post1 = PostFactory(
        author=user,
        business=user.business,
        title='First Post',
        created_at=timezone.make_aware(datetime(2023, 1, 1, 0, 0, 0))
    )
    post2 = PostFactory(
        author=user,
        business=user.business,
        title='Second Post',
        created_at=timezone.make_aware(datetime(2023, 2, 1, 0, 0, 0))
    )
    url = reverse('post-list') + '?ordering=created_at'
    response = authenticated_client.get(url, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['results'][0]['id'] == post1.id
    assert response.data['results'][1]['id'] == post2.id

# ============================
# 커스텀 액션 테스트
# ============================

@pytest.mark.django_db
def test_my_posts(authenticated_client, user):
    """
    'my_posts' 커스텀 액션 테스트
    """
    post1 = PostFactory(author=user)
    post2 = PostFactory(author=user)
    url = reverse('post-my-posts')  # views의 메소드 이름은 my_posts 이지만, reverse 에서는 '-' 사용
    response = authenticated_client.get(url, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) >= 2
    assert any(p['id'] == post1.id for p in response.data['results'])
    assert any(p['id'] == post2.id for p in response.data['results'])
    assert all(p['author'] == user.username for p in response.data['results'])
