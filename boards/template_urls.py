from django.urls import path
from . import views

app_name = 'boards'

urlpatterns = [
    path('', views.BoardMainView.as_view(), name='board_main'),  # 게시판 메인 페이지
    path('posts/create/', views.PostCreateView.as_view(), name='post_create'),  # 게시글 작성 페이지
    path('posts/my_posts/', views.MyPostListView.as_view(), name='my_posts'),  # 내 게시글 페이지
    path('posts/<int:id>/', views.PostDetailView.as_view(), name='post_detail'),  # 게시글 상세 페이지
]
