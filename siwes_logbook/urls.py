from django.urls import path
from . import views

urlpatterns = [
    # Landing & Auth
    path('', views.landing_page, name='landing'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/student/', views.register_student, name='register_student'),
    path('register/supervisor/', views.register_supervisor, name='register_supervisor'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Daily Entries
    path('entry/new/', views.create_entry, name='create_entry'),
    path('entry/<int:pk>/', views.entry_detail, name='entry_detail'),
    path('entry/<int:pk>/edit/', views.edit_entry, name='edit_entry'),
    path('entries/', views.entry_list, name='entry_list'),

    # Evidence
    path('evidence/<int:pk>/delete/', views.delete_evidence, name='delete_evidence'),

    # Weekly Reports
    path('report/new/', views.create_weekly_report, name='create_weekly_report'),
    path('report/<int:pk>/', views.report_detail, name='report_detail'),
    path('report/<int:pk>/edit/', views.edit_weekly_report, name='edit_weekly_report'),
    path('reports/', views.report_list, name='report_list'),

    # Notifications
    path('notifications/', views.notifications_view, name='notifications'),
    path('notification/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/read-all/', views.mark_all_read, name='mark_all_read'),

    # PDF Export
    path('export/pdf/', views.export_logbook_pdf, name='export_pdf'),

    # Profile
    path('profile/', views.profile_view, name='profile'),
]
