import factory
from factory import Faker
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from boards.models import Business, Post, Comment

User = get_user_model()

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = Faker('user_name')
    # email = Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'password123')  # 안전한 비밀번호 설정
    role = 'BUSINESS_MEMBER'  # 기본 역할을 MEMBER로 설정

class BusinessFactory(DjangoModelFactory):
    class Meta:
        model = Business

    name = Faker('company')

class PostFactory(DjangoModelFactory):
    class Meta:
        model = Post

    title = Faker('sentence', nb_words=6)
    content = Faker('paragraph', nb_sentences=3)
    is_public = True
    is_deleted = False
    author = factory.SubFactory(UserFactory)
    business = factory.SubFactory(BusinessFactory)
    
class PublishedPostFactory(PostFactory):
    is_public = True
    is_deleted = False

class DraftPostFactory(PostFactory):
    is_public = False
    is_deleted = False

class DeletedPostFactory(PostFactory):
    is_public = False
    is_deleted = True

class CommentFactory(DjangoModelFactory):
    class Meta:
        model = Comment

    content = Faker('sentence', nb_words=100)
    is_public = True
    is_deleted = False
    author = factory.SubFactory(UserFactory)
    post = factory.SubFactory(PostFactory)