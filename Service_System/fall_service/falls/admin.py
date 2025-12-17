from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import FallEvent, Device


@admin.register(FallEvent)
class FallEventAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'thumbnail_image',
        'location',
        'occurred_at',
        'created_at',
        'is_checked',
        'user',
    ]
    list_filter = [
        'location',
        'is_checked',
        'occurred_at',
        'created_at',
    ]
    search_fields = [
        'location',
        'description',
        'user__username',
    ]
    readonly_fields = [
        'created_at',
        'image_preview',
    ]
    list_editable = ['is_checked']
    date_hierarchy = 'occurred_at'
    ordering = ['-occurred_at']  # 최신순으로 정렬
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('user', 'location', 'description', 'occurred_at', 'is_checked')
        }),
        ('이미지', {
            'fields': ('image', 'image_preview')
        }),
        ('시스템 정보', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def thumbnail_image(self, obj):
        """리스트에서 이미지 썸네일 표시"""
        if obj.image:
            return format_html(
                '<img src="{}" width="80" height="80" style="object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "No Image"
    thumbnail_image.short_description = '이미지'
    
    def image_preview(self, obj):
        """상세 페이지에서 이미지 미리보기"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 500px; max-height: 500px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return "이미지가 없습니다."
    image_preview.short_description = '이미지 미리보기'
    
    def get_queryset(self, request):
        """쿼리셋 최적화"""
        qs = super().get_queryset(request)
        return qs.select_related('user')
    
    actions = ['mark_as_checked', 'mark_as_unchecked']
    
    def mark_as_checked(self, request, queryset):
        """선택된 항목들을 확인됨으로 표시"""
        updated = queryset.update(is_checked=True)
        self.message_user(request, f'{updated}개의 낙상 이벤트가 확인됨으로 표시되었습니다.')
    mark_as_checked.short_description = '선택된 항목을 확인됨으로 표시'
    
    def mark_as_unchecked(self, request, queryset):
        """선택된 항목들을 미확인으로 표시"""
        updated = queryset.update(is_checked=False)
        self.message_user(request, f'{updated}개의 낙상 이벤트가 미확인으로 표시되었습니다.')
    mark_as_unchecked.short_description = '선택된 항목을 미확인으로 표시'


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'token_short', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['user__username', 'token']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def token_short(self, obj):
        """토큰의 일부만 표시"""
        return f"{obj.token[:20]}..." if len(obj.token) > 20 else obj.token
    token_short.short_description = '토큰 (일부)'

