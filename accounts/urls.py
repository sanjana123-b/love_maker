from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profiles/', views.profile_list_view, name='profile_list'),
    path('profiles/<int:pk>/', views.profile_detail_view, name='profile_detail'),
]
