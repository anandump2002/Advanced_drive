# accounts/admin.py

from django.contrib import admin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'student_type', 'phone_number', 'created_at')
    list_filter = ('user_type', 'student_type')
    search_fields = ('user__username', 'user__email', 'phone_number')
    date_hierarchy = 'created_at'

admin.site.register(UserProfile, UserProfileAdmin)