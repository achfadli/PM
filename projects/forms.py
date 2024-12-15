from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Project, ProjectTask, ProjectCategory

class ProjectCategoryForm(forms.ModelForm):
    class Meta:
        model = ProjectCategory
        fields = ['name', 'description', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'slug': forms.TextInput(attrs={'class': 'form-control'})
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title', 'description', 'category', 'status',
            'priority', 'start_date', 'end_date',
            'progress', 'budget', 'team_members'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter project title')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Describe your project')
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'progress': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100
            }),
            'budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'team_members': forms.SelectMultiple(attrs={
                'class': 'form-control select2',
                'multiple': 'multiple'
            })
        }

    def clean(self):
        """
        Validasi khusus untuk form project
        """
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        progress = cleaned_data.get('progress')

        # Validasi tanggal
        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError(_("End date must be after start date"))

        # Validasi progress
        if progress is not None:
            if progress < 0 or progress > 100:
                raise forms.ValidationError(_("Progress must be between 0 and 100"))

        return cleaned_data


class ProjectTaskForm(forms.ModelForm):
    class Meta:
        model = ProjectTask
        fields = [
            'project', 'title', 'description',
            'assigned_to', 'status', 'due_date'
        ]
        widgets = {
            'project': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter task title')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Describe the task')
            }),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }

    def clean(self):
        """
        Validasi khusus untuk form task
        """
        cleaned_data = super().clean()
        project = cleaned_data.get('project')
        due_date = cleaned_data.get('due_date')

        # Validasi tanggal jatuh tempo sesuai dengan proyek
        if project and due_date:
            if project.start_date and due_date < project.start_date:
                raise forms.ValidationError(_("Task due date must be after project start date"))

            if project.end_date and due_date > project.end_date:
                raise forms.ValidationError(_("Task due date must be before or on project end date"))

        return cleaned_data


class ProjectSearchForm(forms.Form):
    """
    Form untuk pencarian dan filter project
    """
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
            'class': 'form-control',
            'type': 'date'
        })
    )

    start_date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )