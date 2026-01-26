from django.contrib import admin
from .models import Goal, DietType, UserProfile


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'display_order', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'code', 'description')
    ordering = ('display_order', 'name')
    list_editable = ('is_active', 'display_order')


@admin.register(DietType)
class DietTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'display_order', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'code', 'description')
    ordering = ('display_order', 'name')
    list_editable = ('is_active', 'display_order')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'diet', 'created_at', 'updated_at')
    list_filter = ('diet', 'goals')
    search_fields = ('user__username', 'user__email', 'description')
    filter_horizontal = ('goals',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Profile Details', {
            'fields': ('profile_image', 'description')
        }),
        ('Preferences', {
            'fields': ('goals', 'diet')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
