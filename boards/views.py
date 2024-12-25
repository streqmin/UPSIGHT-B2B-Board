from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import PostSerializer, CommentSerializer
from .models import Post, Comment
from authentication.models import BusinessMember
from authentication.permissions import IsOwnerOrBusinessAdmin
from django.utils import timezone
from django.views.generic import TemplateView

class BoardMainView(TemplateView):
    template_name = 'boards/home.html'

class PostCreateView(TemplateView):
    template_name = 'boards/post_create.html'

class MyPostListView(TemplateView):
    template_name = 'boards/my_post.html'

class PostDetailView(TemplateView):
    template_name = 'boards/post_detail.html'

# 게시글 관리용 뷰셋
class PostViewSet(viewsets.ModelViewSet):
    """
    Post 모델의 CRUD 기능을 제공하는 뷰셋.
    인증된 사용자만 접근할 수 있으며, 게시글의 소유자 또는 비즈니스 관리자만 수정/삭제할 수 있습니다.
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrBusinessAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_public']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        현재 사용자의 역할에 따라 다른 쿼리셋을 반환.
        - Admin: 소속된 비즈니스의 모든 게시글
        - Member: 자신이 작성한 게시글
        """
        # Swagger 스키마 생성 중인 경우 모든 게시글을 반환하여 예외 방지
        if getattr(self, 'swagger_fake_view', False):
            return Post.objects.all().order_by('-created_at')
        
        user = self.request.user
        if user.role == BusinessMember.BUSINESS_ADMIN:
            return Post.objects.all().order_by('-created_at')
        return Post.objects.filter(Q(is_public=True) | Q(author=user), deleted_at__isnull=True).order_by('-created_at')

    def perform_create(self, serializer):
        """
        게시글 생성 시 author와 business 필드를 자동으로 설정.
        """
        serializer.save(author=self.request.user, business=self.request.user.business)

    def perform_destroy(self, instance):
        """
        게시글 삭제 대신 deleted_at 필드를 현재 시각으로 설정하여 논리적 삭제.
        """
        if instance.deleted_at is not None:
            raise NotFound("이 게시글은 이미 삭제된 상태입니다.")
        
        instance.deleted_at = timezone.now()
        instance.save()

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_posts(self, request):
        """
        현재 사용자가 작성한 모든 게시글을 조회하는 커스텀 액션.
        URL: /api/posts/my_posts/
        """
        user = request.user
        posts = self.get_queryset().filter(author=user)
        page = self.paginate_queryset(posts)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

# 댓글 관리용 뷰셋
class CommentViewSet(viewsets.ModelViewSet):
    """
    Comment 모델의 CRUD 기능을 제공하는 뷰셋.
    인증된 사용자만 접근할 수 있으며, 댓글의 소유자 또는 비즈니스 관리자만 수정/삭제할 수 있습니다.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrBusinessAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['post', 'is_public']
    search_fields = ['content']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        현재 사용자의 역할에 따라 다른 쿼리셋을 반환.
        - Admin: 소속된 비즈니스의 모든 댓글
        - Member: 자신이 작성한 댓글
        """
        # Swagger 스키마 생성 중인 경우 모든 댓글을 반환하여 예외 방지
        if getattr(self, 'swagger_fake_view', False):
            return Comment.objects.all().order_by('-created_at')
        
        user = self.request.user
        if user.role == BusinessMember.BUSINESS_ADMIN:
            return Comment.objects.all().order_by('-created_at')
        return Comment.objects.filter(
            Q(is_public=True) | Q(author=user),
            deleted_at__isnull=True
        ).order_by('-created_at')

    def perform_create(self, serializer):
        """
        댓글 생성 시 author 필드를 자동으로 설정.
        """
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        """
        게시글 삭제 대신 deleted_at 필드를 현재 시각으로 설정하여 논리적 삭제.
        """
        if instance.deleted_at is not None:
            raise NotFound("이 댓글은 이미 삭제된 상태입니다.")
        
        instance.deleted_at = timezone.now()
        instance.save()

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_comments(self, request):
        """
        현재 사용자가 작성한 모든 댓글을 조회하는 커스텀 액션.
        URL: /api/comments/my_comments/
        """
        user = request.user
        comments = self.get_queryset().filter(author=user)
        page = self.paginate_queryset(comments)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
