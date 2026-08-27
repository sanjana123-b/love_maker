from django.contrib import admin
from .models import Profile, ProfilePhoto, ProfilePrompt, InterestTag, BlockRecord, UserReport


class ProfilePhotoInline(admin.TabularInline):
    model = ProfilePhoto
    extra = 1


class ProfilePromptInline(admin.StackedInline):
    model = ProfilePrompt
    extra = 1


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'gender', 'looking_for', 'city', 'zodiac_sign', 'is_verified', 'is_incognito', 'created_at']
    list_filter = ['gender', 'looking_for', 'zodiac_sign', 'is_verified', 'is_incognito']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email', 'city', 'interests']
    inlines = [ProfilePhotoInline, ProfilePromptInline]


@admin.register(InterestTag)
class InterestTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'category']
    list_filter = ['category']
    search_fields = ['name']


@admin.register(BlockRecord)
class BlockRecordAdmin(admin.ModelAdmin):
    list_display = ['blocker', 'blocked_user', 'reason', 'created_at']
    search_fields = ['blocker__username', 'blocked_user__username']


@admin.register(UserReport)
class UserReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'reporter', 'reported_user', 'category', 'status', 'created_at', 'reviewed_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['reporter__username', 'reported_user__username', 'description', 'admin_notes']
    readonly_fields = ['created_at']
    actions = ['mark_as_reviewed', 'mark_as_action_taken', 'mark_as_dismissed']

    @admin.action(description='Mark selected reports as Reviewed')
    def mark_as_reviewed(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='reviewed', reviewed_at=timezone.now())

    @admin.action(description='Mark selected reports as Action Taken')
    def mark_as_action_taken(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='action_taken', reviewed_at=timezone.now())

    @admin.action(description='Dismiss selected reports')
    def mark_as_dismissed(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='dismissed', reviewed_at=timezone.now())
