import pytest
from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
def test_login(api_client, user):
    """
    사용자 로그인 테스트
    """
    url = reverse('token_obtain_pair')  # JWT 토큰 얻기 엔드포인트
    data = {
        'username': user.username,
        'password': 'password123!'  # UserFactory에서 설정한 비밀번호
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
    assert 'refresh' in response.data

@pytest.mark.django_db
def test_login_invalid_username(api_client, user):
    """
    잘못된 사용자 이름으로 로그인 시도 시 401 Unauthorized 응답을 반환하는지 테스트
    """
    url = reverse('token_obtain_pair') 
    data = {
        'username': 'invalid_username',  
        'password': 'password123!'  # 올바른 비밀번호
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert 'detail' in response.data
    assert response.data['detail'] == 'No active account found with the given credentials'

@pytest.mark.django_db
def test_login_invalid_password(api_client, user):
    """
    잘못된 비밀번호로 로그인 시도 시 401 Unauthorized 응답을 반환하는지 테스트
    """
    url = reverse('token_obtain_pair')  # JWT 토큰 얻기 엔드포인트
    data = {
        'username': user.username,
        'password': 'wrong_password'  # 잘못된 비밀번호
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert 'detail' in response.data
    assert response.data['detail'] == 'No active account found with the given credentials'
