# boards/tests/test_comment.py

import pytest
from rest_framework import status
from django.urls import reverse
from boards.models import Comment
from boards.tests.factories import CommentFactory

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
    # comment = Comment.objects.get(author = admin_user)
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
        'is_deleted': False
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
    assert comment.is_deleted == True

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
    assert comment.is_deleted == False

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