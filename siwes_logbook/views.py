from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import Count, Q
from django.core.paginator import Paginator
from datetime import timedelta

from .models import UserProfile, DailyEntry, EntryEvidence, WeeklyReport, Notification
from .forms import (
    StudentRegistrationForm, SupervisorRegistrationForm,
    DailyEntryForm, EvidenceForm, WeeklyReportForm, SupervisorReviewForm
)
from .pdf_utils import generate_logbook_pdf


# ─── Authentication Views ───────────────────────────────────────

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'siwes_logbook/landing.html')


def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name}! Your student account has been created.')
            return redirect('dashboard')
    else:
        form = StudentRegistrationForm()
    return render(request, 'siwes_logbook/register.html', {'form': form, 'role': 'Student'})


def register_supervisor(request):
    if request.method == 'POST':
        form = SupervisorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name}! Your supervisor account has been created.')
            return redirect('dashboard')
    else:
        form = SupervisorRegistrationForm()
    return render(request, 'siwes_logbook/register.html', {'form': form, 'role': 'Supervisor'})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'siwes_logbook/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('landing')


# ─── Dashboard Views ────────────────────────────────────────────

@login_required
def dashboard(request):
    profile = request.user.profile
    if profile.role == 'supervisor':
        return supervisor_dashboard(request)
    return student_dashboard(request)


@login_required
def student_dashboard(request):
    profile = request.user.profile
    entries = DailyEntry.objects.filter(student=request.user)
    reports = WeeklyReport.objects.filter(student=request.user)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False)[:5]

    total_entries = entries.count()
    approved_entries = entries.filter(status='approved').count()
    pending_entries = entries.filter(status='pending').count()
    rejected_entries = entries.filter(status='rejected').count()
    recent_entries = entries[:5]

    total_reports = reports.count()
    approved_reports = reports.filter(status='approved').count()

    context = {
        'profile': profile,
        'total_entries': total_entries,
        'approved_entries': approved_entries,
        'pending_entries': pending_entries,
        'rejected_entries': rejected_entries,
        'recent_entries': recent_entries,
        'total_reports': total_reports,
        'approved_reports': approved_reports,
        'notifications': notifications,
        'unread_count': notifications.count(),
    }
    return render(request, 'siwes_logbook/dashboard_student.html', context)


@login_required
def supervisor_dashboard(request):
    profile = request.user.profile
    assigned_students = UserProfile.objects.filter(supervisor=profile)
    student_users = [sp.user for sp in assigned_students]

    pending_entries = DailyEntry.objects.filter(student__in=student_users, status='pending')
    pending_reports = WeeklyReport.objects.filter(student__in=student_users, status='pending')
    notifications = Notification.objects.filter(recipient=request.user, is_read=False)[:5]

    recently_reviewed = DailyEntry.objects.filter(
        reviewed_by=request.user
    ).order_by('-reviewed_at')[:5]

    context = {
        'profile': profile,
        'assigned_students': assigned_students,
        'student_count': assigned_students.count(),
        'pending_entries': pending_entries,
        'pending_entries_count': pending_entries.count(),
        'pending_reports': pending_reports,
        'pending_reports_count': pending_reports.count(),
        'recently_reviewed': recently_reviewed,
        'notifications': notifications,
        'unread_count': notifications.count(),
    }
    return render(request, 'siwes_logbook/dashboard_supervisor.html', context)


# ─── Daily Entry Views ──────────────────────────────────────────

@login_required
def create_entry(request):
    if request.method == 'POST':
        form = DailyEntryForm(request.POST)
        files = request.FILES.getlist('evidence_files')
        if form.is_valid():
            entry = form.save(commit=False)
            entry.student = request.user
            entry.save()

            for f in files:
                EntryEvidence.objects.create(
                    entry=entry,
                    file=f,
                    caption=f.name
                )

            profile = request.user.profile
            if profile.supervisor:
                Notification.objects.create(
                    recipient=profile.supervisor.user,
                    notification_type='entry_submitted',
                    title='New Logbook Entry',
                    message=f'{request.user.get_full_name()} submitted a new logbook entry for {entry.date}.',
                    link=f'/entry/{entry.pk}/'
                )

            messages.success(request, 'Daily entry submitted successfully!')
            return redirect('entry_list')
    else:
        entries_count = DailyEntry.objects.filter(student=request.user).count()
        initial = {
            'date': timezone.now().date(),
            'day_number': entries_count + 1,
            'week_number': (entries_count // 5) + 1,
        }
        form = DailyEntryForm(initial=initial)

    return render(request, 'siwes_logbook/entry_form.html', {'form': form, 'editing': False})


@login_required
def edit_entry(request, pk):
    entry = get_object_or_404(DailyEntry, pk=pk, student=request.user)
    if entry.status == 'approved':
        messages.warning(request, 'You cannot edit an approved entry.')
        return redirect('entry_detail', pk=pk)

    if request.method == 'POST':
        form = DailyEntryForm(request.POST, instance=entry)
        files = request.FILES.getlist('evidence_files')
        if form.is_valid():
            entry = form.save()
            entry.status = 'pending'
            entry.save()
            for f in files:
                EntryEvidence.objects.create(entry=entry, file=f, caption=f.name)
            messages.success(request, 'Entry updated successfully!')
            return redirect('entry_detail', pk=pk)
    else:
        form = DailyEntryForm(instance=entry)

    return render(request, 'siwes_logbook/entry_form.html', {
        'form': form, 'editing': True, 'entry': entry
    })


@login_required
def entry_list(request):
    profile = request.user.profile
    if profile.role == 'supervisor':
        assigned_students = UserProfile.objects.filter(supervisor=profile)
        student_users = [sp.user for sp in assigned_students]
        entries = DailyEntry.objects.filter(student__in=student_users)
    else:
        entries = DailyEntry.objects.filter(student=request.user)

    status_filter = request.GET.get('status', '')
    if status_filter:
        entries = entries.filter(status=status_filter)

    paginator = Paginator(entries, 10)
    page = request.GET.get('page')
    entries_page = paginator.get_page(page)

    return render(request, 'siwes_logbook/entry_list.html', {
        'entries': entries_page,
        'status_filter': status_filter,
    })


@login_required
def entry_detail(request, pk):
    entry = get_object_or_404(DailyEntry, pk=pk)
    profile = request.user.profile

    if profile.role == 'student' and entry.student != request.user:
        messages.error(request, 'You do not have permission to view this entry.')
        return redirect('entry_list')

    evidence = entry.evidence.all()
    review_form = None

    if profile.role == 'supervisor' and entry.status == 'pending':
        if request.method == 'POST':
            review_form = SupervisorReviewForm(request.POST)
            if review_form.is_valid():
                entry.status = review_form.cleaned_data['status']
                entry.supervisor_comment = review_form.cleaned_data['supervisor_comment']
                entry.reviewed_by = request.user
                entry.reviewed_at = timezone.now()
                entry.save()

                notif_type = 'entry_approved' if entry.status == 'approved' else 'entry_rejected'
                Notification.objects.create(
                    recipient=entry.student,
                    notification_type=notif_type,
                    title=f'Entry {entry.status.title()}',
                    message=f'Your logbook entry for {entry.date} has been {entry.status} by {request.user.get_full_name()}.',
                    link=f'/entry/{entry.pk}/'
                )

                messages.success(request, f'Entry has been {entry.status}.')
                return redirect('entry_detail', pk=pk)
        else:
            review_form = SupervisorReviewForm()

    return render(request, 'siwes_logbook/entry_detail.html', {
        'entry': entry,
        'evidence': evidence,
        'review_form': review_form,
    })


@login_required
def delete_evidence(request, pk):
    evidence = get_object_or_404(EntryEvidence, pk=pk)
    if evidence.entry.student != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('entry_list')
    entry_pk = evidence.entry.pk
    evidence.delete()
    messages.success(request, 'Evidence file removed.')
    return redirect('entry_detail', pk=entry_pk)


# ─── Weekly Report Views ────────────────────────────────────────

@login_required
def create_weekly_report(request):
    if request.method == 'POST':
        form = WeeklyReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.student = request.user
            report.student_signature_date = timezone.now().date()
            report.save()

            profile = request.user.profile
            if profile.supervisor:
                Notification.objects.create(
                    recipient=profile.supervisor.user,
                    notification_type='report_submitted',
                    title='New Weekly Report',
                    message=f'{request.user.get_full_name()} submitted weekly report for Week {report.week_number}.',
                    link=f'/report/{report.pk}/'
                )

            messages.success(request, 'Weekly report submitted successfully!')
            return redirect('report_list')
    else:
        report_count = WeeklyReport.objects.filter(student=request.user).count()
        today = timezone.now().date()
        initial = {
            'week_number': report_count + 1,
            'start_date': today - timedelta(days=today.weekday()),
            'end_date': today - timedelta(days=today.weekday()) + timedelta(days=4),
        }
        form = WeeklyReportForm(initial=initial)

    return render(request, 'siwes_logbook/report_form.html', {'form': form, 'editing': False})


@login_required
def edit_weekly_report(request, pk):
    report = get_object_or_404(WeeklyReport, pk=pk, student=request.user)
    if report.status == 'approved':
        messages.warning(request, 'You cannot edit an approved report.')
        return redirect('report_detail', pk=pk)

    if request.method == 'POST':
        form = WeeklyReportForm(request.POST, instance=report)
        if form.is_valid():
            report = form.save()
            report.status = 'pending'
            report.save()
            messages.success(request, 'Report updated successfully!')
            return redirect('report_detail', pk=pk)
    else:
        form = WeeklyReportForm(instance=report)

    return render(request, 'siwes_logbook/report_form.html', {
        'form': form, 'editing': True, 'report': report
    })


@login_required
def report_list(request):
    profile = request.user.profile
    if profile.role == 'supervisor':
        assigned_students = UserProfile.objects.filter(supervisor=profile)
        student_users = [sp.user for sp in assigned_students]
        reports = WeeklyReport.objects.filter(student__in=student_users)
    else:
        reports = WeeklyReport.objects.filter(student=request.user)

    status_filter = request.GET.get('status', '')
    if status_filter:
        reports = reports.filter(status=status_filter)

    paginator = Paginator(reports, 10)
    page = request.GET.get('page')
    reports_page = paginator.get_page(page)

    return render(request, 'siwes_logbook/report_list.html', {
        'reports': reports_page,
        'status_filter': status_filter,
    })


@login_required
def report_detail(request, pk):
    report = get_object_or_404(WeeklyReport, pk=pk)
    profile = request.user.profile

    if profile.role == 'student' and report.student != request.user:
        messages.error(request, 'You do not have permission to view this report.')
        return redirect('report_list')

    review_form = None
    if profile.role == 'supervisor' and report.status == 'pending':
        if request.method == 'POST':
            review_form = SupervisorReviewForm(request.POST)
            if review_form.is_valid():
                report.status = review_form.cleaned_data['status']
                report.supervisor_comment = review_form.cleaned_data['supervisor_comment']
                report.reviewed_by = request.user
                report.reviewed_at = timezone.now()
                report.supervisor_signature_date = timezone.now().date()
                report.save()

                notif_type = 'report_approved' if report.status == 'approved' else 'report_rejected'
                Notification.objects.create(
                    recipient=report.student,
                    notification_type=notif_type,
                    title=f'Weekly Report {report.status.title()}',
                    message=f'Your Week {report.week_number} report has been {report.status} by {request.user.get_full_name()}.',
                    link=f'/report/{report.pk}/'
                )

                messages.success(request, f'Report has been {report.status}.')
                return redirect('report_detail', pk=pk)
        else:
            review_form = SupervisorReviewForm()

    return render(request, 'siwes_logbook/report_detail.html', {
        'report': report,
        'review_form': review_form,
    })


# ─── Notifications ──────────────────────────────────────────────

@login_required
def notifications_view(request):
    all_notifs = Notification.objects.filter(recipient=request.user)
    paginator = Paginator(all_notifs, 15)
    page = request.GET.get('page')
    notifs_page = paginator.get_page(page)

    return render(request, 'siwes_logbook/notifications.html', {'notifications': notifs_page})


@login_required
def mark_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.save()
    if notif.link:
        return redirect(notif.link)
    return redirect('notifications')


@login_required
def mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('notifications')


# ─── PDF Export ──────────────────────────────────────────────────

@login_required
def export_logbook_pdf(request):
    profile = request.user.profile
    entries = DailyEntry.objects.filter(student=request.user).order_by('date')
    reports = WeeklyReport.objects.filter(student=request.user).order_by('week_number')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="SIWES_Logbook_{request.user.get_full_name().replace(" ", "_")}.pdf"'

    generate_logbook_pdf(response, request.user, profile, entries, reports)
    return response


# ─── Profile ────────────────────────────────────────────────────

@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        profile.phone = request.POST.get('phone', profile.phone)
        profile.department = request.POST.get('department', profile.department)
        profile.institution = request.POST.get('institution', profile.institution)
        profile.company_name = request.POST.get('company_name', profile.company_name)
        profile.company_address = request.POST.get('company_address', profile.company_address)
        profile.bio = request.POST.get('bio', profile.bio)

        if 'profile_photo' in request.FILES:
            profile.profile_photo = request.FILES['profile_photo']

        training_start = request.POST.get('training_start_date')
        training_end = request.POST.get('training_end_date')
        if training_start:
            profile.training_start_date = training_start
        if training_end:
            profile.training_end_date = training_end

        profile.save()

        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name = request.POST.get('last_name', request.user.last_name)
        request.user.email = request.POST.get('email', request.user.email)
        request.user.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    return render(request, 'siwes_logbook/profile.html', {'profile': profile})
