from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from .models import Project, ProjectTask
from .models import Project, ProjectTask, ProjectCategory
from .forms import ProjectForm, ProjectTaskForm, ProjectSearchForm, ProjectCategoryForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ProjectCategory
from .forms import ProjectCategoryForm

class ProjectListView(LoginRequiredMixin, ListView):
    """
    Halaman daftar project dengan fitur search dan filter
    """
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 10

    def get_queryset(self):
        # Dapatkan project yang dimiliki atau di-team
        queryset = Project.objects.filter(
            Q(owner=self.request.user) | Q(team_members=self.request.user)
        ).distinct()

        # Inisialisasi form pencarian
        self.search_form = ProjectSearchForm(self.request.GET)

        # Filtering berdasarkan form pencarian
        if self.search_form.is_valid():
            # Filter berdasarkan query pencarian
            search_query = self.search_form.cleaned_data.get('search_query')
            if search_query:
                queryset = queryset.filter(
                    Q(title__icontains=search_query) |
                    Q(description__icontains=search_query)
                )

            # Filter berdasarkan kategori
            category = self.search_form.cleaned_data.get('category')
            if category:
                queryset = queryset.filter(category=category)

            # Filter berdasarkan status
            status = self.search_form.cleaned_data.get('status')
            if status:
                queryset = queryset.filter(status=status)

            # Filter berdasarkan prioritas
            priority = self.search_form.cleaned_data.get('priority')
            if priority:
                queryset = queryset.filter(priority=priority)

            # Filter berdasarkan rentang tanggal
            start_date_from = self.search_form.cleaned_data.get('start_date_from')
            start_date_to = self.search_form.cleaned_data.get('start_date_to')
            if start_date_from and start_date_to:
                queryset = queryset.filter(
                    start_date__range=[start_date_from, start_date_to]
                )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = self.search_form
        context['total_projects'] = self.get_queryset().count()
        context['title'] = 'My Projects'
        return context


class ProjectDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Halaman detail project
    """
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'

    def test_func(self):
        # Pastikan user adalah pemilik atau anggota tim
        project = self.get_object()
        return self.request.user == project.owner or \
            self.request.user in project.team_members.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        tasks = project.tasks.all()

        # Hitung statistik
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status='done').count()
        task_completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        context.update({
            'tasks': tasks,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'task_completion_percentage': task_completion_percentage,
            'title': project.title
        })
        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    """
    Halaman untuk membuat project baru
    """
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('project_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(
            self.request,
            f'Project "{form.instance.title}" has been created successfully.'
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Project'
        return context


class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Halaman untuk mengupdate project
    """
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'

    def test_func(self):
        # Pastikan hanya pemilik yang bisa update
        project = self.get_object()
        return self.request.user == project.owner

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request,
            f'Project "{form.instance.title}" has been updated successfully.'
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Project'
        return context


class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Hapus project
    """
    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('project_list')

    def test_func(self):
        # Pastikan hanya pemilik yang bisa delete
        project = self.get_object()
        return self.request.user == project.owner

    def form_valid(self, form):
        project_title = self.object.title
        messages.success(
            self.request,
            f'Project "{project_title}" has been deleted successfully.'
        )
        return super().form_valid(form)


class ProjectTaskCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Tambah task baru ke project
    """
    model = ProjectTask
    form_class = ProjectTaskForm
    template_name = 'projects/task_form.html'

    def test_func(self):
        # Pastikan user adalah pemilik atau anggota tim
        project = Project.objects.get(pk=self.kwargs['project_pk'])
        return self.request.user == project.owner or \
            self.request.user in project.team_members.all()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        project = Project.objects.get(pk=self.kwargs['project_pk'])
        kwargs['project'] = project
        return kwargs

    def form_valid(self, form):
        project = Project.objects.get(pk=self.kwargs['project_pk'])
        form.instance.project = project
        messages.success(
            self.request,
            f'Task "{form.instance.title}" has been added to project.'
        )
        return super().form_valid(form)

        def get_success_url(self):
            return reverse_lazy('project_detail', kwargs={'pk': self.kwargs['project_pk']})

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['project'] = Project.objects.get(pk=self.kwargs['project_pk'])
            context['title'] = 'Add New Task'
            return context

    class ProjectTaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
        """
        Update task yang sudah ada
        """
        model = ProjectTask
        form_class = ProjectTaskForm
        template_name = 'projects/task_form.html'

        def test_func(self):
            # Pastikan user adalah pemilik project atau anggota tim
            task = self.get_object()
            return (self.request.user == task.project.owner or
                    self.request.user in task.project.team_members.all())

        def get_form_kwargs(self):
            kwargs = super().get_form_kwargs()
            kwargs['project'] = self.object.project
            return kwargs

        def form_valid(self, form):
            messages.success(
                self.request,
                f'Task "{form.instance.title}" has been updated successfully.'
            )
            return super().form_valid(form)

        def get_success_url(self):
            return reverse_lazy('project_detail', kwargs={'pk': self.object.project.pk})

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['project'] = self.object.project
            context['title'] = 'Update Task'
            return context

    class ProjectTaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
        """
        Hapus task dari project
        """
        model = ProjectTask
        template_name = 'projects/task_confirm_delete.html'

        def test_func(self):
            # Pastikan user adalah pemilik project
            task = self.get_object()
            return self.request.user == task.project.owner

        def form_valid(self, form):
            project = self.object.project
            task_title = self.object.title
            messages.success(
                self.request,
                f'Task "{task_title}" has been deleted successfully.'
            )
            return super().form_valid(form)

        def get_success_url(self):
            return reverse_lazy('project_detail', kwargs={'pk': self.object.project.pk})

    class ProjectCategoryCreateView(LoginRequiredMixin, CreateView):
        """
        Halaman untuk membuat kategori project baru
        """
        model = ProjectCategory
        form_class = ProjectCategoryForm
        template_name = 'projects/category_form.html'
        success_url = reverse_lazy('project_category_list')

        def form_valid(self, form):
            messages.success(
                self.request,
                'Project category has been created successfully.'
            )
            return super().form_valid(form)

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['title'] = 'Create New Project Category'
            return context

    class ProjectCategoryListView(LoginRequiredMixin, ListView):
        """
        Halaman daftar kategori project
        """
        model = ProjectCategory
        template_name = 'projects/category_list.html'
        context_object_name = 'categories'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['title'] = 'Project Categories'
            return context

    class ProjectCategoryUpdateView(LoginRequiredMixin, UpdateView):
        """
        Halaman untuk mengupdate kategori project
        """
        model = ProjectCategory
        form_class = ProjectCategoryForm
        template_name = 'projects/category_form.html'
        success_url = reverse_lazy('project_category_list')

        def form_valid(self, form):
            messages.success(
                self.request,
                'Project category has been updated successfully.'
            )
            return super().form_valid(form)

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['title'] = 'Update Project Category'
            return context

    class ProjectCategoryDeleteView(LoginRequiredMixin, DeleteView):
        """
        Hapus kategori project
        """
        model = ProjectCategory
        template_name = 'projects/category_confirm_delete.html'
        success_url = reverse_lazy('project_category_list')

        def form_valid(self, form):
            messages.success(
                self.request,
                'Project category has been deleted successfully.'
            )
            return super().form_valid(form)

    class ProjectTeamManagementView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
        """
        Manajemen anggota tim project
        """
        model = Project
        template_name = 'projects/team_management.html'
        fields = ['team_members']

        def test_func(self):
            # Hanya pemilik project yang bisa mengelola tim
            project = self.get_object()
            return self.request.user == project.owner

        def get_form(self, form_class=None):
            form = super().get_form(form_class)
            # Filter pilihan anggota tim
            form.fields['team_members'].queryset = self.request.user.get_all_users()
            return form

        def form_valid(self, form):
            messages.success(
                self.request,
                'Project team members have been updated successfully.'
            )
            return super().form_valid(form)

        def get_success_url(self):
            return reverse_lazy('project_detail', kwargs={'pk': self.object.pk})

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['title'] = 'Manage Project Team'
            return context



class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'projects/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Project yang dimiliki atau di-team
        user_projects = Project.objects.filter(
            Q(owner=self.request.user) | Q(team_members=self.request.user)
        ).distinct()

    from django.contrib.auth.mixins import LoginRequiredMixin
    from django.views.generic import TemplateView
    from django.db.models import Q
    from .models import Project, ProjectTask

    class DashboardView(LoginRequiredMixin, TemplateView):
        template_name = 'projects/dashboard.html'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)

            # Project yang dimiliki atau di-team
            user_projects = Project.objects.filter(
                Q(owner=self.request.user) | Q(team_members=self.request.user)
            ).distinct()

            # Tambahkan method untuk menghitung progress
            def calculate_project_progress(project):
                tasks = project.tasks.all()
                if not tasks:
                    return 0
                completed_tasks = tasks.filter(status='done').count()
                return (completed_tasks / tasks.count()) * 100

            # Tambahkan progress ke setiap project
            for project in user_projects:
                project.progress = calculate_project_progress(project)

            # Statistik
            context.update({
                'total_projects': user_projects.count(),
                'ongoing_projects': user_projects.filter(status='in_progress').count(),
                'completed_projects': user_projects.filter(status='completed').count(),
                'total_tasks': ProjectTask.objects.filter(project__in=user_projects).count(),
                'recent_projects': list(user_projects.order_by('-created_at')[:5]),  # Konversi ke list
            })
            return context





@login_required
def project_category_list(request):
    categories = ProjectCategory.objects.all()
    return render(request, 'projects/project_category_list.html', {
        'categories': categories,
        'title': 'Project Categories'
    })


@login_required
def project_category_create(request):
    if request.method == 'POST':
        form = ProjectCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully.')
            return redirect('project_category_list')
    else:
        form = ProjectCategoryForm()

    return render(request, 'projects/project_category_form.html', {
        'form': form,
        'title': 'Create Project Category'
    })


@login_required
def project_category_detail(request, slug):
    category = get_object_or_404(ProjectCategory, slug=slug)
    return render(request, 'projects/project_category_detail.html', {
        'category': category,
        'title': f'Category: {category.get_name_display()}'
    })


@login_required
def project_category_update(request, slug):
    category = get_object_or_404(ProjectCategory, slug=slug)

    if request.method == 'POST':
        form = ProjectCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('project_category_list')
    else:
        form = ProjectCategoryForm(instance=category)

    return render(request, 'projects/project_category_form.html', {
        'form': form,
        'title': f'Update Category: {category.get_name_display()}'
    })


@login_required
def project_category_delete(request, slug):
    category = get_object_or_404(ProjectCategory, slug=slug)

    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('project_category_list')

    return render(request, 'projects/project_category_confirm_delete.html', {
        'category': category,
        'title': f'Delete Category: {category.get_name_display()}'
    })
