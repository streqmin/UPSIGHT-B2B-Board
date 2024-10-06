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

## 🖥️ models.py

> | 개체             | 모델명         |
> | ---------------- | -------------- |
> | 고객사           | Business       |
> | 고객사 소속 회원 | BusinessMember |
> | 게시글           | Post           |
> | 댓글             | Comment        |

## 🖥️ views.py

> | 도메인      | 뷰셋 이름       | 상속 뷰셋              |
> | ----------- | --------------- | ---------------------- |
> | 사용자 등록 | RegisterView    | generics.CreateAPIView |
> | 고객사      | BusinessViewSet | viewsets.ModelViewSet  |
> | 게시글      | PostViewSet     | viewsets.ModelViewSet  |
> | 댓글        | CommentViewSet  | viewsets.ModelViewSet  |

-   DRF의 query_set 설정을 활용하여 권한 별 접근 데이터에 차등을 구현함
-   permission은 일반 member 와 admin 으로 구분됨

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

---

## 📜 **API 목록 및 설명**

| **Endpoint**                 | **HTTP Method**                    | **Description**                                              | **Query Parameters**                                                                                   | **Permissions**                       | **View**                     |
| ---------------------------- | ---------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------ | ------------------------------------- | ---------------------------- |
| `/api/auth/register/`        | `POST`                             | 새로운 **BusinessMember (사용자)**를 등록합니다.             | **Body Parameters:** <br> - `username` <br> - `password` <br> - `email` <br> - 기타 사용자 관련 필드들 | `AllowAny`                            | `RegisterView`               |
| `/api/auth/login/`           | `POST`                             | JWT 액세스 및 리프레시 토큰을 획득합니다.                    | **Body Parameters:** <br> - `username` <br> - `password`                                               | `AllowAny`                            | `TokenObtainPairView`        |
| `/api/auth/refresh/`         | `POST`                             | JWT 액세스 토큰을 갱신합니다.                                | **Body Parameters:** <br> - `refresh`                                                                  | `AllowAny`                            | `TokenRefreshView`           |
| `/api/businesses/`           | `GET` / `POST`                     | 모든 **Business**를 조회하거나 새로운 비즈니스를 생성합니다. | - `name` (필터) <br> - `search` <br> - `ordering`                                                      | `IsAuthenticated` & `IsBusinessAdmin` | `BusinessViewSet`            |
| `/api/businesses/{id}/`      | `GET` / `PUT` / `PATCH` / `DELETE` | 특정 **Business**의 상세 정보를 조회, 수정, 삭제합니다.      | `{id}`: Business ID                                                                                    | `IsAuthenticated` & `IsBusinessAdmin` | `BusinessViewSet`            |
| `/api/posts/`                | `GET` / `POST`                     | 모든 **Post**를 조회하거나 새로운 게시글을 생성합니다.       | - `is_public` (필터) <br> - `search` <br> - `ordering`                                                 | `IsAuthenticated`                     | `PostViewSet`                |
| `/api/posts/{id}/`           | `GET` / `PUT` / `PATCH` / `DELETE` | 특정 **Post**의 상세 정보를 조회, 수정, 삭제합니다.          | `{id}`: Post ID                                                                                        | `IsOwnerOrBusinessAdmin`              | `PostViewSet`                |
| `/api/posts/my_posts/`       | `GET`                              | 현재 인증된 사용자가 작성한 모든 **Post**를 조회합니다.      | - **Pagination Parameters:** <br> &nbsp;&nbsp;- `page` <br> &nbsp;&nbsp;- `page_size`                  | `IsAuthenticated`                     | `PostViewSet.my_posts`       |
| `/api/comments/`             | `GET` / `POST`                     | 모든 **Comment**를 조회하거나 새로운 댓글을 생성합니다.      | - `post` (필터) <br> - `is_public` (필터) <br> - `search` <br> - `ordering`                            | `IsAuthenticated`                     | `CommentViewSet`             |
| `/api/comments/{id}/`        | `GET` / `PUT` / `PATCH` / `DELETE` | 특정 **Comment**의 상세 정보를 조회, 수정, 삭제합니다.       | `{id}`: Comment ID                                                                                     | `IsOwnerOrBusinessAdmin`              | `CommentViewSet`             |
| `/api/comments/my_comments/` | `GET`                              | 현재 인증된 사용자가 작성한 모든 **Comment**를 조회합니다.   | - **Pagination Parameters:** <br> &nbsp;&nbsp;- `page` <br> &nbsp;&nbsp;- `page_size`                  | `IsAuthenticated`                     | `CommentViewSet.my_comments` |

---

## **API 권한 요약**

| **Permission Class**     | **설명**                                                                         |
| ------------------------ | -------------------------------------------------------------------------------- |
| `AllowAny`               | 인증 여부와 상관없이 모든 사용자가 접근할 수 있습니다.                           |
| `IsAuthenticated`        | 인증된 사용자만 접근할 수 있습니다.                                              |
| `IsBusinessAdmin`        | **비즈니스 관리자(Admin)**만 접근할 수 있습니다.                                 |
| `IsOwnerOrBusinessAdmin` | **댓글이나 게시글의 소유자** 또는 **비즈니스 관리자**만 수정/삭제할 수 있습니다. |

---

## **쿼리 파라미터 필터링 예시**

### **BusinessViewSet**

| **Query Parameter** | **Description**                                            |
| ------------------- | ---------------------------------------------------------- |
| `name`              | 특정 이름으로 비즈니스 필터링                              |
| `search`            | `name`, `address`, `phone_number`, `website` 필드에서 검색 |
| `ordering`          | `name` 기준 정렬                                           |

### **PostViewSet**

| **Query Parameter** | **Description**                  |
| ------------------- | -------------------------------- |
| `is_public`         | 공개 여부로 게시글 필터링        |
| `search`            | `title`, `content` 필드에서 검색 |
| `ordering`          | `created_at`, `title` 기준 정렬  |

### **CommentViewSet**

| **Query Parameter** | **Description**              |
| ------------------- | ---------------------------- |
| `post`              | 특정 게시글 ID로 댓글 필터링 |
| `is_public`         | 공개 여부로 댓글 필터링      |
| `search`            | `content` 필드에서 검색      |
| `ordering`          | `created_at` 기준 정렬       |

---
