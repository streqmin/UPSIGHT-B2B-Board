import pytest
from rest_framework import status
from django.urls import reverse
from boards.models import BusinessMember

@pytest.mark.django_db
def test_register_user(api_client, business):
    """
    사용자 등록 API 테스트
    """
    url = reverse('auth_register')
    data = {
        'username': 'testuser',
        'password': 'testpassword123!',
        'password2': 'testpassword123!',
        'role': 'member',
        'business': business.id
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['username'] == data['username']
    assert 'password' not in response.data  # 패스워드는 노출되지 않아야 함
    assert BusinessMember.objects.filter(username='testuser').exists()

@pytest.mark.django_db
def test_register_password_mismatch(api_client, business):
    """
    사용자 등록 시 password와 password2가 일치하지 않으면 400 Bad Request 응답을 반환하는지 테스트
    """
    url = reverse('auth_register')
    data = {
        'username': 'testuser',
        'password': 'password123!',
        'password2': 'differentpassword',
        'role': 'member',
        'business': business.id
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'password' in response.data
    assert response.data['password'] == ["Password fields didn't match."]

@pytest.mark.django_db
def test_register_invalid_role(api_client, business):
    """
    사용자 등록 시 유효하지 않은 role 값을 입력하면 400 Bad Request 응답을 반환하는지 테스트
    """
    url = reverse('auth_register')  # RegisterView의 URL 이름
    data = {
        'username': 'testuser',
        'password': 'password123!',
        'password2': 'password123!',
        'role': 'invalid_role',  # 유효하지 않은 역할
        'business': business.id
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'role' in response.data
    assert response.data['role'] == ['"invalid_role" is not a valid choice.']

@pytest.mark.django_db
def test_register_user_duplicate_username(api_client, user):
    """
    중복된 사용자 이름으로 등록 시 실패 테스트
    """
    url = reverse('auth_register')
    data = {
        'username': user.username,  # 기존 사용자 이름 사용
        'password': 'newpassword123',
        'role': 'member'
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'username' in response.data

@pytest.mark.django_db
def test_register_user_invalid_data(api_client):
    """
    잘못된 데이터로 등록 시 실패 테스트
    """
    url = reverse('auth_register')
    data = {
        'username': '',  # 빈 사용자 이름
        'password': 'short',  # 너무 짧은 패스워드
        'role': 'INVALID_ROLE'  # 잘못된 역할
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'username' in response.data
    assert 'password' in response.data
    assert 'role' in response.data