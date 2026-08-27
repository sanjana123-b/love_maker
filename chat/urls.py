from django.urls import path
from . import views

urlpatterns = [
    path('', views.inbox_view, name='inbox'),
    path('<int:match_id>/', views.conversation_view, name='conversation'),
    path('api/icebreakers/<int:match_id>/', views.icebreakers_api_view, name='icebreakers_api'),
    path('api/react/<int:message_id>/', views.message_reaction_api_view, name='message_reaction_api'),
]
