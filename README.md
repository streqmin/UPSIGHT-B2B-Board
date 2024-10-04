# UPSIGHT B2B Board

## 📚 사용된 라이브러리

```shell
# Django, JWT, Swagger ...
pip install django
pip install djangorestframework
pip install django-filter
pip install djangorestframework-simplejwt
pip install django-cors-headers
pip install drf-yasg
# pytest, factoryboy ...
pip install pytest
pip install pytest-django
pip install pytest-factoryboy
pip install factory_boy
pip install Faker
pip install pytest-cov
# Postgresql ...
pip install psycopg2-binary
```

## 🖥️ API 설명

> models.py
> | 개체 | 모델명 |
> | ---------------- | -------------- |
> | 고객사 | Business |
> | 고객사 소속 회원 | BusinessMember |
> | 게시글 | Post |
> | 댓글 | Comment |

> views.py
> | 개체 | 모델명 |
> | ---------------- | -------------- |
> | 고객사 | Business |
> | 고객사 소속 회원 | BusinessMember |
> | 게시글 | Post |
> | 댓글 | Comment |

## 👥 JWT 설정

```python
# /miniintern/settings.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type'
}
```
