from django.urls import path
from . import views

urlpatterns = [
    path('quiz/', views.quiz_view, name='quiz'),
    path('like/<int:user_id>/', views.like_user_view, name='like_user'),
    path('matches/', views.matches_list_view, name='matches'),
]
