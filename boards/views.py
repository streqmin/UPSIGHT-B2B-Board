from rest_framework import generics, viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import (
    RegisterSerializer,
    BusinessSerializer,
    PostSerializer,
    CommentSerializer
)
from .models import Business, Post, Comment, BusinessMember
from .permissions import IsBusinessAdmin, IsOwnerOrBusinessAdmin, IsOwnerOrReadOnly

# 사용자 등록을 위한 뷰
class RegisterView(generics.CreateAPIView):
    """
    새로운 BusinessMember (사용자)을 등록하는 API 엔드포인트.
    모든 사용자가 접근할 수 있습니다.
    """
    queryset = BusinessMember.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    # def create(self, request, *args, **kwargs):
    #     """
    #     사용자 등록 시 추가적인 로직이 필요하다면 여기에 작성.
    #     현재는 기본적인 생성 로직을 사용합니다.
    #     """
    #     return super().create(request, *args, **kwargs)

# 비즈니스 관리용 뷰셋
class BusinessViewSet(viewsets.ModelViewSet):
    """
    Business 모델의 CRUD (생성, 조회, 수정, 삭제) 기능을 제공하는 뷰셋.
    오직 비즈니스 관리자(Admin)만 접근할 수 있습니다.
    """
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [permissions.IsAuthenticated, IsBusinessAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name']
    search_fields = ['name', 'address', 'phone_number', 'website']
    ordering_fields = ['name']

# 게시글 관리용 뷰셋
class PostViewSet(viewsets.ModelViewSet):
    """
    Post 모델의 CRUD 기능을 제공하는 뷰셋.
    인증된 사용자만 접근할 수 있으며, 게시글의 소유자 또는 비즈니스 관리자만 수정/삭제할 수 있습니다.
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrBusinessAdmin, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_public']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'title']

    def get_queryset(self):
        """
        현재 사용자의 역할에 따라 다른 쿼리셋을 반환.
        - Admin: 소속된 비즈니스의 모든 게시글
        - Member: 자신이 작성한 게시글
        """
        user = self.request.user
        if user.role == BusinessMember.BUSINESS_ADMIN:
            return Post.objects.filter(business=user.business, is_deleted=False)
        return Post.objects.filter(author=user, is_deleted=False)

    def perform_create(self, serializer):
        """
        게시글 생성 시 author와 business 필드를 자동으로 설정.
        """
        serializer.save(author=self.request.user, business=self.request.user.business)

    # def perform_update(self, serializer):
    #     """
    #     게시글 업데이트 시 추가적인 로직이 필요하다면 여기에 작성.
    #     """
    #     serializer.save()

    def perform_destroy(self, instance):
        """
        게시글 삭제 대신 is_deleted 필드를 True로 설정하여 논리적 삭제.
        """
        instance.is_deleted = True
        instance.save()

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_posts(self, request):
        """
        현재 사용자가 작성한 모든 게시글을 조회하는 커스텀 액션.
        URL: /api/posts/my_posts/
        """
        user = request.user
        posts = self.get_queryset()
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

# 댓글 관리용 뷰셋
class CommentViewSet(viewsets.ModelViewSet):
    """
    Comment 모델의 CRUD 기능을 제공하는 뷰셋.
    인증된 사용자만 접근할 수 있으며, 댓글의 소유자 또는 비즈니스 관리자만 수정/삭제할 수 있습니다.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrBusinessAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_public']
    search_fields = ['content']
    ordering_fields = ['created_at']

    def get_queryset(self):
        """
        현재 사용자의 역할에 따라 다른 쿼리셋을 반환.
        - Admin: 소속된 비즈니스의 모든 댓글
        - Member: 자신이 작성한 댓글
        """
        user = self.request.user
        if user.role == BusinessMember.BUSINESS_ADMIN:
            return Comment.objects.filter(post__business=user.business, is_deleted=False)
        return Comment.objects.filter(author=user, is_deleted=False)

    def perform_create(self, serializer):
        """
        댓글 생성 시 author 필드를 자동으로 설정.
        """
        serializer.save(author=self.request.user)

    # def perform_update(self, serializer):
    #     """
    #     댓글 업데이트 시 추가적인 로직이 필요하다면 여기에 작성.
    #     """
    #     serializer.save()

    def perform_destroy(self, instance):
        """
        댓글 삭제 대신 is_deleted 필드를 True로 설정하여 논리적 삭제.
        """
        instance.is_deleted = True
        instance.save()

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_comments(self, request):
        """
        현재 사용자가 작성한 모든 댓글을 조회하는 커스텀 액션.
        URL: /api/comments/my_comments/
        """
        comments = self.get_queryset()
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)
