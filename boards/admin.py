# boards/admin.py

from django.contrib import admin
from .models import Business, BusinessMember, Post, Comment
from django.contrib.auth.admin import UserAdmin

class BusinessMemberAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('business', 'role')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('business', 'role')}),
    )
    list_display = ['username', 'first_name', 'last_name', 'business', 'role', 'is_staff']
    list_filter = ['role', 'business']
    search_fields = ['username', 'first_name', 'last_name']
    ordering = ['username']

admin.site.register(Business, admin.ModelAdmin)
admin.site.register(BusinessMember, BusinessMemberAdmin)
admin.site.register(Post)
admin.site.register(Comment)
