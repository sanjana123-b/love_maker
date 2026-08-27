from django.contrib import admin
from .models import QuizQuestion, QuizAnswer, Like, Match, SwipeAction, DateProposal


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'text', 'category']
    list_filter = ['category']
    search_fields = ['text']


@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'selected_option', 'created_at']
    list_filter = ['selected_option', 'question__category']
    search_fields = ['user__username', 'question__text']


@admin.register(SwipeAction)
class SwipeActionAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'action', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['from_user__username', 'to_user__username']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'is_superlike', 'created_at']
    list_filter = ['is_superlike', 'created_at']
    search_fields = ['from_user__username', 'to_user__username']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['id', 'user1', 'user2', 'is_active', 'created_at', 'unmatched_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user1__username', 'user2__username']


@admin.register(DateProposal)
class DateProposalAdmin(admin.ModelAdmin):
    list_display = ['id', 'match', 'proposed_by', 'title', 'status', 'suggested_date', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['proposed_by__username', 'title', 'details']
