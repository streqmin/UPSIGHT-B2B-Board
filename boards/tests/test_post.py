# boards/tests/test_post.py

import pytest
from rest_framework import status
from django.urls import reverse
from boards.models import Post
from boards.tests.factories import PostFactory
from datetime import datetime
from django.utils import timezone

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
        'business': business.id,  # 적절한 비즈니스 ID로 수정 필요
        'title': 'Unauthorized Post',
        'content': 'This should not be created.',
        'is_public': True
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

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
def test_deleted_post_not_in_list(authenticated_client, deleted_post):
    """
    is_deleted=True인 게시글이 목록 조회 시 제외되는지 테스트
    """
    url = reverse('post-list')
    response = authenticated_client.get(url, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert not any(p['id'] == deleted_post.id for p in response.data['results'])

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

@pytest.mark.django_db
def test_pagination_posts(authenticated_client, user):
    """
    게시글 페이지네이션 테스트
    """
    for _ in range(60):
        PostFactory(author=user)
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
    url = reverse('post-list') + '?page=2&limit=20'  # 총 25개 게시글, 페이지 2은 5개
    response = authenticated_client.get(url, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 5
    assert response.data['next'] is None
    assert response.data['previous'] is not None

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
def test_update_users_post_business_admin(admin_authenticated_client, post):
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

@pytest.mark.django_db
def test_delete_post(authenticated_client, post):
    """
    게시글 삭제 테스트 (게시글 소유자)
    """
    url = reverse('post-detail', args=[post.id])
    response = authenticated_client.delete(url, format='json')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    post.refresh_from_db()
    assert post.is_deleted == True

@pytest.mark.django_db
def test_delete_post_non_owner(non_owner_authenticated_client, post):
    """
    게시글 삭제 시도 (비소유자 사용자)
    """
    url = reverse('post-detail', args=[post.pk])
    response = non_owner_authenticated_client.delete(url, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN
    post.refresh_from_db()
    assert post.is_deleted == False

@pytest.mark.django_db
def test_delete_post_unauthenticated(api_client, post):
    """
    비인증 사용자가 게시글 삭제 시도 시 401 Unauthorized 응답을 받는지 테스트
    """
    url = reverse('post-detail', args=[post.id])
    response = api_client.delete(url, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_my_posts(authenticated_client, user):
    """
    'my_posts' 커스텀 액션 테스트
    """
    post1 = PostFactory(author=user)
    post2 = PostFactory(author=user)
    url = reverse('post-my-posts')  # views의 메소드 이름은 my_posts 이지만, reverse 에서는 '_' -> '-'
    response = authenticated_client.get(url, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) >= 2
    assert any(p['id'] == post1.id for p in response.data['results'])
    assert any(p['id'] == post2.id for p in response.data['results'])