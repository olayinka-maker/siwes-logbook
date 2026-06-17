from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('supervisor', 'Supervisor'),
        ('coordinator', 'IT Coordinator'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    department = models.CharField(max_length=150, blank=True)
    institution = models.CharField(max_length=200, blank=True)
    matric_number = models.CharField(max_length=30, blank=True, help_text="For students only")
    staff_id = models.CharField(max_length=30, blank=True, help_text="For supervisors only")
    phone = models.CharField(max_length=20, blank=True)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    supervisor = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='students', help_text="Assigned supervisor (for students)"
    )
    training_start_date = models.DateField(null=True, blank=True)
    training_end_date = models.DateField(null=True, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    company_address = models.TextField(blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.role})"

    @property
    def total_entries(self):
        return self.user.daily_entries.count()

    @property
    def approved_entries(self):
        return self.user.daily_entries.filter(status='approved').count()

    @property
    def pending_entries(self):
        return self.user.daily_entries.filter(status='pending').count()

    @property
    def training_weeks(self):
        if self.training_start_date and self.training_end_date:
            delta = self.training_end_date - self.training_start_date
            return delta.days // 7
        return 0


class DailyEntry(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_entries')
    date = models.DateField(default=timezone.now)
    day_number = models.PositiveIntegerField(default=1, help_text="Day number in training")
    week_number = models.PositiveIntegerField(default=1, help_text="Week number in training")
    title = models.CharField(max_length=200, help_text="Brief title of today's activities")
    activities = models.TextField(help_text="Detailed description of activities carried out today")
    skills_acquired = models.TextField(blank=True, help_text="Skills, tools, or knowledge gained today")
    challenges = models.TextField(blank=True, help_text="Challenges faced and how you overcame them")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    supervisor_comment = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_entries'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['student', 'date']
        verbose_name = "Daily Entry"
        verbose_name_plural = "Daily Entries"

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.date} ({self.status})"


class EntryEvidence(models.Model):
    entry = models.ForeignKey(DailyEntry, on_delete=models.CASCADE, related_name='evidence')
    file = models.FileField(upload_to='evidence/%Y/%m/%d/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evidence for {self.entry}"

    @property
    def is_image(self):
        return self.file.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))

    @property
    def filename(self):
        return self.file.name.split('/')[-1]


class WeeklyReport(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weekly_reports')
    week_number = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    summary = models.TextField(help_text="Overall summary of the week's activities")
    achievements = models.TextField(blank=True, help_text="Key achievements and milestones")
    problems_encountered = models.TextField(blank=True, help_text="Problems encountered during the week")
    plans_for_next_week = models.TextField(blank=True, help_text="Plans and objectives for next week")
    student_signature_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    supervisor_comment = models.TextField(blank=True)
    supervisor_signature_date = models.DateField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_weekly_reports'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-week_number']
        unique_together = ['student', 'week_number']

    def __str__(self):
        return f"{self.student.get_full_name()} - Week {self.week_number} ({self.status})"


class Notification(models.Model):
    TYPE_CHOICES = [
        ('entry_submitted', 'Entry Submitted'),
        ('entry_approved', 'Entry Approved'),
        ('entry_rejected', 'Entry Rejected'),
        ('report_submitted', 'Report Submitted'),
        ('report_approved', 'Report Approved'),
        ('report_rejected', 'Report Rejected'),
        ('general', 'General'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='general')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"
