from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/photo/upload/', views.upload_photo_view, name='upload_photo'),
    path('profile/photo/<int:photo_id>/delete/', views.delete_photo_view, name='delete_photo'),
    path('profile/prompt/save/', views.save_prompt_view, name='save_prompt'),
    path('profile/prompt/<int:prompt_id>/delete/', views.delete_prompt_view, name='delete_prompt'),
    path('profiles/', views.profile_list_view, name='profile_list'),
    path('profile/<int:pk>/', views.profile_detail_view, name='profile_detail'),
    
    # Trust & Safety
    path('block/<int:user_id>/', views.block_user_view, name='block_user'),
    path('unblock/<int:user_id>/', views.unblock_user_view, name='unblock_user'),
    path('blocked-list/', views.blocked_list_view, name='blocked_list'),
    path('report/<int:user_id>/', views.report_user_view, name='report_user'),
]
