from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(  
    title="B2B Django Board API",
    default_version='v1',
    description="API documentation for the B2B Django Board system"),
    
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/board/', include('boards.urls')),
    path('api/auth/', include('authentication.urls')),
    
    path('auth/', include('authentication.template_urls')),
    path('board/', include('boards.template_urls')),
    
    # API 문서화
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
