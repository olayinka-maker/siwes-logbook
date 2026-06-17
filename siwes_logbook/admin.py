from django.contrib import admin
from .models import UserProfile, DailyEntry, EntryEvidence, WeeklyReport, Notification


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'department', 'institution', 'matric_number', 'staff_id']
    list_filter = ['role', 'department']
    search_fields = ['user__first_name', 'user__last_name', 'matric_number', 'staff_id']


@admin.register(DailyEntry)
class DailyEntryAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'title', 'status', 'reviewed_by', 'reviewed_at']
    list_filter = ['status', 'date']
    search_fields = ['student__first_name', 'student__last_name', 'title']
    date_hierarchy = 'date'


@admin.register(EntryEvidence)
class EntryEvidenceAdmin(admin.ModelAdmin):
    list_display = ['entry', 'file', 'caption', 'uploaded_at']


@admin.register(WeeklyReport)
class WeeklyReportAdmin(admin.ModelAdmin):
    list_display = ['student', 'week_number', 'start_date', 'end_date', 'status']
    list_filter = ['status']
    search_fields = ['student__first_name', 'student__last_name']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']
    search_fields = ['recipient__username', 'title']
