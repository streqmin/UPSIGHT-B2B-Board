# boards/tests/test_business.py

import pytest
from rest_framework import status
from django.urls import reverse
from boards.models import Business

@pytest.mark.django_db
def test_create_business(admin_authenticated_client):
    """
    비즈니스 생성 테스트 (관리자 권한)
    """
    url = reverse('business-list')  # routers.py에서 BusinessViewSet에 대한 name이 'business-list'라고 가정
    data = {
        'name': 'Test Business'
    }
    response = admin_authenticated_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert Business.objects.filter(name='Test Business').exists()

@pytest.mark.django_db
def test_create_business_non_admin(authenticated_client):
    """
    비관리자가 비즈니스 생성 시도 시 실패 테스트
    """
    url = reverse('business-list')
    data = {
        'name': 'Unauthorized Business',
        # 'address': '456 Unauthorized St',
        # 'phone_number': '987-654-3210',
        # 'website': 'https://www.unauthorized.com'
    }
    response = authenticated_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not Business.objects.filter(name='Unauthorized Business').exists()

@pytest.mark.django_db
def test_list_business(admin_authenticated_client, business):
    """
    비즈니스 목록 조회 테스트 (관리자 권한)
    """
    url = reverse('business-list')
    response = admin_authenticated_client.get(url, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) >= 1  # 최소 하나 이상의 비즈니스가 존재
    assert any(b['id'] == business.id for b in response.data['results'])

@pytest.mark.django_db
def test_update_business(admin_authenticated_client, business):
    """
    비즈니스 수정 테스트 (관리자 권한)
    """
    url = reverse('business-detail', args=[business.id])
    data = {
        'name': 'Updated Business',
        # 'address': '789 Updated St',
        # 'phone_number': '555-555-5555',
        # 'website': 'https://www.updated.com'
    }
    response = admin_authenticated_client.put(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    business.refresh_from_db()
    assert business.name == 'Updated Business'

@pytest.mark.django_db
def test_delete_business(admin_authenticated_client, business):
    """
    비즈니스 삭제 테스트 (관리자 권한)
    """
    url = reverse('business-detail', args=[business.id])
    response = admin_authenticated_client.delete(url, format='json')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Business.objects.filter(id=business.id).exists()

@pytest.mark.django_db
def test_delete_business_non_admin(authenticated_client, business):
    """
    비관리자가 비즈니스 삭제 시도 시 실패 테스트
    """
    url = reverse('business-detail', args=[business.id])
    response = authenticated_client.delete(url, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Business.objects.filter(id=business.id).exists()