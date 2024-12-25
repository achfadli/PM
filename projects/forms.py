from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Project, ProjectTask, ProjectCategory


class ProjectCategoryForm(forms.ModelForm):
    class Meta:
        model = ProjectCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ProjectForm(forms.ModelForm):
    team_members = forms.ModelMultipleChoiceField(
        queryset=None,  # Akan diset di __init__
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
    )

    class Meta:
        model = Project
        fields = [
            'title',
            'description',
            'category',
            'status',
            'priority',
            'start_date',
            'end_date',
            'budget',
            'progress'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control datepicker', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control datepicker', 'type': 'date'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control'}),
            'progress': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Hanya menampilkan user yang terkait
        if user:
            self.fields['team_members'].queryset = user.get_all_users()  # Sesuaikan dengan method di User model

        # Set initial untuk team_members jika sedang update
        if self.instance.pk:
            self.fields['team_members'].initial = self.instance.team_members.all()

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # Validasi tanggal
        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError(_("End date must be after start date"))

        return cleaned_data


class ProjectTaskForm(forms.ModelForm):
    class Meta:
        model = ProjectTask
        fields = [
            'title',
            'description',
            'assigned_to',
            'status',
            'priority',
            'due_date'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control datepicker', 'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        # Filter assigned_to berdasarkan project members
        if project:
            self.fields['assigned_to'].queryset = project.team_members.all()

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')

        # Validasi tanggal jatuh tempo
        if due_date and due_date < timezone.now().date():
            raise ValidationError(_("Due date cannot be in the past"))

        return due_date


class ProjectSearchForm(forms.Form):
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Search projects...')
        })
    )

    category = forms.ModelChoiceField(
        queryset=ProjectCategory.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    status = forms.ChoiceField(
        choices=[('', _('All Statuses'))] + Project.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    priority = forms.ChoiceField(
        choices=[('', _('All Priorities'))] + Project.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    start_date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker',
            'type': 'date',
            'placeholder': _('From Date')
        })
    )

    start_date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker',
            'type': 'date',
            'placeholder': _('To Date')
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date_from = cleaned_data.get('start_date_from')
        start_date_to = cleaned_data.get('start_date_to')

        # Validasi rentang tanggal
        if start_date_from and start_date_to:
            if start_date_from > start_date_to:
                raise ValidationError(_("From date must be before To date"))

        return cleaned_data

