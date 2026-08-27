from django.urls import path
from . import views

urlpatterns = [
    path('discover/', views.discover_swipe_view, name='discover_swipe'),
    path('api/swipe/', views.swipe_api_view, name='swipe_api'),
    path('api/radar/<int:user_id>/', views.compatibility_radar_api_view, name='compatibility_radar_api'),
    path('unmatch/<int:match_id>/', views.unmatch_user_view, name='unmatch_user'),
    path('propose-date/<int:match_id>/', views.propose_date_view, name='propose_date'),
    path('respond-date/<int:proposal_id>/', views.respond_date_proposal_view, name='respond_date_proposal'),
    path('quiz/', views.quiz_view, name='quiz'),
    path('love-match/', views.love_match_view, name='love_match'),
    path('like/<int:user_id>/', views.like_user_view, name='like_user'),
    path('matches/', views.matches_list_view, name='matches'),
]
