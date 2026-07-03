from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.decorators import staff_required
from .models import Project, ProjectPhase, Amenity
from .forms import ProjectForm, ProjectImageFormSet


def project_list(request):
    from apps.core.utils import get_sortable_context
    projects = Project.objects.all()
    template = 'projects/admin_project_list.html' if request.user.is_authenticated and request.user.is_staff_or_above() else 'projects/project_list.html'
    is_staff = request.user.is_authenticated and request.user.is_staff_or_above()
    if is_staff:
        ctx = get_sortable_context(request, projects, default_sort='name',
                                   allowed_fields=['name', 'location', 'created_at'],
                                   search_fields=['name', 'location'],
                                   per_page=15)
    else:
        ctx = get_sortable_context(request, projects, default_sort='name',
                                   allowed_fields=['name', 'location'],
                                   search_fields=['name', 'location'],
                                   per_page=12)
    return render(request, template, ctx)


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    template = 'projects/admin_project_detail.html' if request.user.is_authenticated and request.user.is_staff_or_above() else 'projects/project_detail.html'
    return render(request, template, {'project': project})


@login_required
@staff_required
def project_create(request):
    form = ProjectForm()
    formset = ProjectImageFormSet()
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save()
            formset = ProjectImageFormSet(request.POST, request.FILES, instance=project)
            if formset.is_valid():
                formset.save()
            messages.success(request, 'Project created successfully.')
            return redirect('projects:project_detail', slug=project.slug)
    return render(request, 'projects/project_form.html', {'form': form, 'formset': formset, 'title': 'Create Project'})


@login_required
@staff_required
def project_edit(request, slug):
    project = get_object_or_404(Project, slug=slug)
    form = ProjectForm(instance=project)
    formset = ProjectImageFormSet(instance=project)
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        formset = ProjectImageFormSet(request.POST, request.FILES, instance=project)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Project updated successfully.')
            return redirect('projects:project_detail', slug=project.slug)
    return render(request, 'projects/project_form.html', {'form': form, 'formset': formset, 'title': 'Edit Project'})


@login_required
@staff_required
def project_delete(request, slug):
    project = get_object_or_404(Project, slug=slug)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully.')
        return redirect('projects:project_list')
    return render(request, 'components/confirm_delete.html', {'object': project})
