from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'gender', 'city', 'age', 'created_at']
    list_filter = ['gender', 'city', 'looking_for']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'city', 'interests']
    readonly_fields = ['created_at', 'updated_at']
