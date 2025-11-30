from django.contrib import admin
from .models import PollModel, VoteRecord, Category, PollAnalytics

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'description']
    search_fields = ['name', 'description']
    list_filter = ['name']

@admin.register(PollModel)
class PollModelAdmin(admin.ModelAdmin):
    list_display = ['question', 'created_by', 'category', 'status', 'total_votes', 'created_at', 'expires_at']
    list_filter = ['status', 'category', 'created_at', 'is_anonymous']
    search_fields = ['question', 'description']
    readonly_fields = ['created_at', 'updated_at', 'total_votes']
    fieldsets = (
        ('Poll Information', {
            'fields': ('question', 'description', 'category', 'created_by')
        }),
        ('Options', {
            'fields': ('op1', 'op2', 'op3')
        }),
        ('Settings', {
            'fields': ('status', 'expires_at', 'is_anonymous')
        }),
        ('Vote Counts', {
            'fields': ('op1c', 'op2c', 'op3c', 'total_votes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(VoteRecord)
class VoteRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'poll', 'choice', 'voted_at']
    list_filter = ['choice', 'voted_at', 'poll__category']
    search_fields = ['user__username', 'poll__question']
    readonly_fields = ['voted_at']

@admin.register(PollAnalytics)
class PollAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['poll', 'views_count', 'unique_voters', 'last_viewed']
    readonly_fields = ['views_count', 'unique_voters', 'last_viewed']