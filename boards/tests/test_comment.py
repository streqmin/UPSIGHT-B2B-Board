# boards/tests/test_comment.py

import pytest
from rest_framework import status
from django.urls import reverse
from boards.models import Comment
from boards.tests.factories import CommentFactory
from django.utils import timezone

@pytest.mark.django_db
def test_create_comment(authenticated_client, post, user):
    """
    댓글 생성 테스트 (일반 사용자)
    """
    url = reverse('comment-list')  # routers.py에서 CommentViewSet에 대한 이름이 'comment-list'라고 가정
    data = {
        'content': 'This is a test comment.',
        'post': post.id,
        'is_public': True
    }
    response = authenticated_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    comment = Comment.objects.get(content='This is a test comment.')
    assert comment.author == user
    assert comment.post == post

@pytest.mark.django_db
def test_create_comment_business_admin(admin_authenticated_client, post, admin_user):
    """
    비즈니스 관리자가 댓글 생성 테스트
    """
    url = reverse('comment-list')
    data = {
        'content': 'Admin Comment.',
        'post': post.id,
        'is_public': False
    }
    response = admin_authenticated_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    comment = Comment.objects.get(content='Admin Comment.')
    assert comment.author == admin_user
    assert comment.post == post

@pytest.mark.django_db
def test_list_comments(authenticated_client, comment):
    """
    댓글 목록 조회 테스트 (일반 사용자)
    """
    url = reverse('comment-list')
    response = authenticated_client.get(url, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert any(c['id'] == comment.id for c in response.data['results'])

@pytest.mark.django_db
def test_retrieve_comment(authenticated_client, comment):
    """
    특정 댓글 조회 테스트 (일반 사용자)
    """
    url = reverse('comment-detail', args=[comment.id])
    response = authenticated_client.get(url, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['content'] == comment.content

@pytest.mark.django_db
def test_retrieve_comments_by_post_id(authenticated_client, user, other_user, post):
    """
    특정 게시글 조회 시 해당 게시글의 모든 공개되고 삭제되지 않은 댓글이 반환되는지 테스트
    """
    comment1 = CommentFactory(post=post, author=user)
    comment2 = CommentFactory(post=post, author=other_user)
    deleted_comment = CommentFactory(post=post, author=user, deleted_at = timezone.now())
    private_comment = CommentFactory(post=post, author=user, is_public=False)
    
    url = reverse('comment-list')
    response = authenticated_client.get(url, {'post': post.id}, format='json')
    
    assert response.status_code == status.HTTP_200_OK
    assert 'results' in response.data
    assert len(response.data['results']) == 2  # 삭제되거나 비공개인 댓글은 포함되지 않음
    
    returned_comment_ids = [comment['id'] for comment in response.data['results']]
    assert comment1.id in returned_comment_ids
    assert comment2.id in returned_comment_ids
    assert deleted_comment.id not in returned_comment_ids
    assert private_comment.id not in returned_comment_ids

@pytest.mark.django_db
def test_retrieve_comments_by_post_id_as_admin(admin_authenticated_client, user, other_user, post):
    """
    특정 게시글 조회 시 해당 게시글의 모든 공개되고 삭제되지 않은 댓글이 반환되는지 테스트
    """
    comment1 = CommentFactory(post=post, author=user)
    comment2 = CommentFactory(post=post, author=other_user)
    deleted_comment = CommentFactory(post=post, author=user, deleted_at = timezone.now())
    private_comment = CommentFactory(post=post, author=user, is_public=False)
    
    url = reverse('comment-list')
    response = admin_authenticated_client.get(url, {'post': post.id}, format='json')
    
    assert response.status_code == status.HTTP_200_OK
    assert 'results' in response.data
    assert len(response.data['results']) == 4  # 삭제되거나 비공개인 댓글은 포함되지 않음
    
    returned_comment_ids = [comment['id'] for comment in response.data['results']]
    assert comment1.id in returned_comment_ids
    assert comment2.id in returned_comment_ids
    assert deleted_comment.id in returned_comment_ids
    assert private_comment.id in returned_comment_ids

@pytest.mark.django_db
def test_retrieve_comments_by_nonexistent_post(authenticated_client, post):
    """
    댓글이 존재하지 않는 게시글의 댓글을 조회하려 할 때 0개의 댓글이 반환되는지 테스트.
    """
    # API 엔드포인트 설정 (존재하지 않는 게시글 ID)
    url = reverse('comment-list')
    response = authenticated_client.get(url, {'post': post.id}, format='json')  # 9999는 존재하지 않는 ID
    
    # 응답 검증
    assert response.status_code == status.HTTP_200_OK
    assert 'results' in response.data
    assert len(response.data['results']) == 0

@pytest.mark.django_db
def test_update_comment(authenticated_client, comment):
    """
    댓글 수정 테스트 (댓글 소유자)
    """
    url = reverse('comment-detail', args=[comment.id])
    data = {
        'content': 'Updated comment content.',
        'is_public': False,
        'post': comment.post.id  # 포스트 ID는 변경하지 않도록 유지
    }
    response = authenticated_client.put(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    comment.refresh_from_db()
    assert comment.content == 'Updated comment content.'
    assert comment.is_public == False

@pytest.mark.django_db
def test_update_comment_non_owner(non_owner_authenticated_client, comment):
    """
    댓글 수정 시도 (비소유자 사용자)
    """
    url = reverse('comment-detail', args=[comment.id])
    data = {
        'content': 'Hacked comment content.',
        'is_public': True,
        'deleted_at': None
    }
    response = non_owner_authenticated_client.put(url, data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN
    comment.refresh_from_db()
    assert comment.content != 'Hacked comment content.'

@pytest.mark.django_db
def test_delete_comment(authenticated_client, comment):
    """
    댓글 삭제 테스트 (댓글 소유자)
    """
    url = reverse('comment-detail', args=[comment.id])
    response = authenticated_client.delete(url, format='json')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    comment.refresh_from_db()
    assert comment.deleted_at

@pytest.mark.django_db
def test_delete_comment_non_owner(non_owner_authenticated_client, comment):
    """
    댓글 삭제 시도 (비소유자 사용자)
    """
    client = non_owner_authenticated_client
    url = reverse('comment-detail', args=[comment.id])
    response = client.delete(url, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN
    comment.refresh_from_db()
    assert comment.deleted_at is None

@pytest.mark.django_db
def test_my_comments(authenticated_client, user):
    """
    'my_comments' 커스텀 액션 테스트
    """
    comment1 = CommentFactory(author=user)
    comment2 = CommentFactory(author=user)
    url = reverse('comment-my-comments')  # views의 메소드 이름은 my_comments 이지만, reverse 에서는 '_' -> '-'
    response = authenticated_client.get(url, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) >= 2
    assert any(c['id'] == comment1.id for c in response.data['results'])
    assert any(c['id'] == comment2.id for c in response.data['results'])
    assert all(p['author'] == user.username for p in response.data['results'])