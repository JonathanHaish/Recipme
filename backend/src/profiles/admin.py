from django.contrib import admin
from .models import UserProfile, Goal, DietType


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'display_order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    list_editable = ['is_active', 'display_order']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'display_order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DietType)
class DietTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'display_order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    list_editable = ['is_active', 'display_order']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'display_order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'diet', 'get_goals', 'created_at', 'updated_at']
    list_filter = ['diet', 'goals', 'created_at']
    search_fields = ['user__username', 'user__email', 'description']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['goals']  # Better UI for ManyToMany selection
    
    def get_goals(self, obj):
        """Display goals as comma-separated list"""
        return ", ".join([goal.name for goal in obj.goals.all()])
    get_goals.short_description = 'Goals'