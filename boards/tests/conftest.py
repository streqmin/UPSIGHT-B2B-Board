# boards/tests/conftest.py

import pytest
from rest_framework.test import APIClient
from boards.tests.factories import *

@pytest.fixture
def api_client():
    """Django REST Framework의 APIClient 인스턴스를 반환"""
    return APIClient()

@pytest.fixture
def user(db, business):
    """일반 사용자 인스턴스를 반환하는 Fixture"""
    return UserFactory(business = business)

@pytest.fixture
def other_user(db, business):
    """비소유자 사용자 인스턴스를 반환하는 Fixture"""
    return UserFactory(business = business)

@pytest.fixture
def admin_user(db, business):
    """비즈니스 관리자 사용자 인스턴스를 반환하는 Fixture"""
    return UserFactory(role='admin', business = business)

@pytest.fixture
def business(db):
    """Business 인스턴스를 반환하는 Fixture"""
    return BusinessFactory()

@pytest.fixture
def authenticated_client(api_client, user):
    """소유자 사용자로 인증된 클라이언트를 반환하는 Fixture"""
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def non_owner_authenticated_client(api_client, other_user):
    """비소유자 사용자로 인증된 클라이언트를 반환하는 Fixture"""
    api_client.force_authenticate(user=other_user)
    return api_client

@pytest.fixture
def admin_authenticated_client(api_client, admin_user):
    """비즈니스 관리자 사용자로 인증된 클라이언트를 반환하는 Fixture"""
    api_client.force_authenticate(user=admin_user)
    return api_client

@pytest.fixture
def post(db, user, business):
    """Post 인스턴스를 반환하는 Fixture"""
    return PostFactory(author=user, business=business)

@pytest.fixture
def published_post(db, user, business):
    """PublishedPost 인스턴스를 반환하는 Fixture"""
    return PublishedPostFactory(author=user, business=business)

@pytest.fixture
def draft_post(db, user, business):
    """DraftPost 인스턴스를 반환하는 Fixture"""
    return DraftPostFactory(author=user, business=business)

@pytest.fixture
def deleted_post(db, user, business):
    """DeletedPost 인스턴스를 반환하는 Fixture"""
    return DeletedPostFactory(author=user, business=business)

@pytest.fixture
def comment(db, user, post):
    """Comment 인스턴스를 반환하는 Fixture"""
    return CommentFactory(author=user, post=post)
