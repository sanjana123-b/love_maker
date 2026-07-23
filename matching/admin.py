from django.contrib import admin
from .models import QuizQuestion, QuizAnswer, Like, Match


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'category']
    list_filter = ['category']


@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'selected_option']
    list_filter = ['selected_option']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'created_at']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['user1', 'user2', 'created_at']
