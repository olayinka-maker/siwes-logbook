from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, DailyEntry, WeeklyReport, EntryEvidence


class StudentRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    matric_number = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'e.g. CSC/2020/001'}))
    department = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'placeholder': 'e.g. Computer Science'}))
    institution = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'placeholder': 'e.g. University of Lagos'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))
    company_name = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'placeholder': 'Company/Organization Name'}))
    company_address = forms.CharField(required=False, widget=forms.Textarea(attrs={'placeholder': 'Company Address', 'rows': 3}))
    training_start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    training_end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Choose a username'
        self.fields['password1'].widget.attrs['placeholder'] = 'Create Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                role='student',
                matric_number=self.cleaned_data['matric_number'],
                department=self.cleaned_data['department'],
                institution=self.cleaned_data['institution'],
                phone=self.cleaned_data.get('phone', ''),
                company_name=self.cleaned_data.get('company_name', ''),
                company_address=self.cleaned_data.get('company_address', ''),
                training_start_date=self.cleaned_data.get('training_start_date'),
                training_end_date=self.cleaned_data.get('training_end_date'),
            )
        return user


class SupervisorRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    staff_id = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'Staff ID'}))
    department = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'placeholder': 'Department'}))
    institution = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'placeholder': 'Institution Name'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Choose a username'
        self.fields['password1'].widget.attrs['placeholder'] = 'Create Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                role='supervisor',
                staff_id=self.cleaned_data['staff_id'],
                department=self.cleaned_data['department'],
                institution=self.cleaned_data['institution'],
                phone=self.cleaned_data.get('phone', ''),
            )
        return user


class DailyEntryForm(forms.ModelForm):
    class Meta:
        model = DailyEntry
        fields = ['date', 'day_number', 'week_number', 'title', 'activities', 'skills_acquired', 'challenges']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'title': forms.TextInput(attrs={'placeholder': 'Brief title of today\'s activities'}),
            'activities': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Describe in detail the activities you carried out today...'}),
            'skills_acquired': forms.Textarea(attrs={'rows': 4, 'placeholder': 'List the skills, tools, technologies or knowledge you gained today...'}),
            'challenges': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe any challenges you faced and how you overcame them...'}),
            'day_number': forms.NumberInput(attrs={'min': 1}),
            'week_number': forms.NumberInput(attrs={'min': 1}),
        }


class EvidenceForm(forms.ModelForm):
    class Meta:
        model = EntryEvidence
        fields = ['file', 'caption']
        widgets = {
            'caption': forms.TextInput(attrs={'placeholder': 'Brief description of this evidence file'}),
        }


class WeeklyReportForm(forms.ModelForm):
    class Meta:
        model = WeeklyReport
        fields = ['week_number', 'start_date', 'end_date', 'summary', 'achievements', 'problems_encountered', 'plans_for_next_week']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'summary': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Overall summary of this week\'s activities...'}),
            'achievements': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Key achievements, milestones and successes this week...'}),
            'problems_encountered': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Problems you encountered and how you addressed them...'}),
            'plans_for_next_week': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Your objectives and plans for the coming week...'}),
        }


class SupervisorReviewForm(forms.Form):
    STATUS_CHOICES = [
        ('approved', 'Approve'),
        ('rejected', 'Reject'),
    ]
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.RadioSelect())
    supervisor_comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Add your comments here (required if rejecting)...'})
    )
