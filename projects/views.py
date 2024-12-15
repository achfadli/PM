from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Project, ProjectTask, ProjectCategory
from .forms import (
    ProjectForm,
    ProjectTaskForm,
    ProjectSearchForm,
    ProjectCategoryForm
)


@login_required
def project_list(request):
    """
    Halaman daftar project dengan fitur search dan filter
    """
    projects = Project.objects.filter(
        Q(owner=request.user) | Q(team_members=request.user)
    ).distinct()

    search_form = ProjectSearchForm(request.GET)
    if search_form.is_valid():
        # Filter berdasarkan query pencarian
        search_query = search_form.cleaned_data.get('search_query')
        if search_query:
            projects = projects.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # Filter berdasarkan kategori
        category = search_form.cleaned_data.get('category')
        if category:
            projects = projects.filter(category=category)

        # Filter berdasarkan status
        status = search_form.cleaned_data.get('status')
        if status:
            projects = projects.filter(status=status)

        # Filter berdasarkan prioritas
        priority = search_form.cleaned_data.get('priority')
        if priority:
            projects = projects.filter(priority=priority)

        # Filter berdasarkan rentang tanggal
        start_date_from = search_form.cleaned_data.get('start_date_from')
        start_date_to = search_form.cleaned_data.get('start_date_to')
        if start_date_from and start_date_to:
            projects = projects.filter(
                start_date__range=[start_date_from, start_date_to]
            )

    # Pagination
    paginator = Paginator(projects, 10)  # 10 project per halaman
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'projects': page_obj,
        'search_form': search_form,
        'total_projects': projects.count(),
        'page_obj': page_obj,
        'title': ('My Projects')
    }
    return render(request, 'projects/project_list.html', context)


@login_required
def project_detail(request, project_id):
    """
    Halaman detail project
    """
    project = get_object_or_404(
        Project,
        id=project_id,
        Q(owner=request.user) | Q(team_members=request.user)
    )

    # Ambil tasks untuk project ini
    tasks = project.tasks.all()

    # Hitung statistik
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='done').count()
    task_completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    context = {
        'project': project,
        'tasks': tasks,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'task_completion_percentage': task_completion_percentage,
        'title': project.title
    }
    return render(request, 'projects/project_detail.html', context)


@login_required
def create_project(request):
    """
    Halaman untuk membuat project baru
    """
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()

            # Simpan many-to-many fields
            form.save_m2m()

            messages.success(
                request,
                'Project "{}" has been created successfully.'.format(project.title)
            )
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm()

    context = {
        'form': form,
        'title': ('Create New Project')
    }
    return render(request, 'projects/project_form.html', context)


@login_required
def update_project(request, project_id):
    """
    Halaman untuk mengupdate project
    """
    project = get_object_or_404(
        Project,
        id=project_id,
        Q(owner=request.user) | Q(team_members=request.user)
    )

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            updated_project = form.save()
            messages.success(
                request,
                ('Project "{}" has been updated successfully.').format(updated_project.title)
            )
            return redirect('project_detail', project_id=updated_project.id)
    else:
        form = ProjectForm(instance=project)

    context = {
        'form': form,
        'project': project,
        'title': ('Update Project')
    }
    return render(request, 'projects/project_form.html', context)


@login_required
def delete_project(request, project_id):
    """
    Hapus project
    """
    project = get_object_or_404(
        Project,
        id=project_id,
        owner=request.user
    )

    if request.method == 'POST':
        project_title = project.title
        project.delete()
        messages.success(
            request,
            ('Project "{}" has been deleted successfully.').format(project_title)
        )
        return redirect('project_list')

    context = {
        'project': project,
        'title': ('Delete Project')
    }
    return render(request, 'projects/project_confirm_delete.html', context)


@login_required
def create_project_task(request, project_id):
    """
    Tambah task baru ke project
    """
    project = get_object_or_404(
        Project,
        id=project_id,
        Q(owner=request.user) | Q(team_members=request.user)
    )

    if request.method == 'POST':
        form = ProjectTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()

            messages.success(
                request,
                ('Task "{}" has been added to project.').format(task.title)
            )
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectTaskForm(initial={'project': project})

    context = {
        'form': form,
        'project': project,
        'title': ('Add New Task')
    }
    return render(request, 'projects/task_form.html', context)


@login_required
def update_project_task(request, task_id):
    """
    Update task yang sudah ada
    """
    task = get_object_or_404(
        ProjectTask,
        id=task_id,
        project__owner=request.user
    )

    if request.method == 'POST':
        form = ProjectTaskForm(request.POST, instance=task)
        if form.is_valid():
            updated_task = form.save()
            messages.success(
                request,
                ('Task "{}" has been updated successfully.').format(updated_task.title)
            )
            return redirect('project_detail', project_id=task.project.id)
    else:
        form = ProjectTaskForm(instance=task)

    context = {
        'form': form,
        'task': task,
        'title': ('Update Task')
    }
    return render(request, 'projects/task_form.html', context)


@login_required
def delete_project_task(request, task_id):
    """
    Hapus task dari project
    """
    task = get_object_or_404(
        ProjectTask,
        id=task_id,
        project__owner=request.user
    )
    project = task.project

    if request.method == 'POST':
        task_title = task.title
        task.delete()
        messages.success(
            request,
            ('Task "{}" has been deleted successfully.').format(task_title)
        )
        return redirect('project_detail', project_id=project.id)

    context = {
        'task': task,
        'project': project,
        'title': ('Delete Task')
    }
    return render(request, 'projects/task_confirm_delete.html', context)