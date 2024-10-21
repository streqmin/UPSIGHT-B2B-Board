from django.db import models
from django.contrib.auth.models import AbstractUser

class Business(models.Model):
    name = models.CharField(max_length=255)

class BusinessMember(AbstractUser):
    BUSINESS_ADMIN = 'admin'
    BUSINESS_MEMBER = 'member'

    ROLE_CHOICES = [
        (BUSINESS_ADMIN, 'Business Admin'),
        (BUSINESS_MEMBER, 'Business Member'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=BUSINESS_MEMBER)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='members', null=True, blank=True)
