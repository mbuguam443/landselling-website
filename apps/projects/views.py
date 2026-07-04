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
    ctx['meta_description'] = 'Explore land development projects by Prime Lands Ltd. Find prime locations in Kenya with verified plots and flexible payment plans.'
    ctx['og_title'] = 'Our Projects - Prime Lands Ltd'
    ctx['og_description'] = 'Discover ongoing and completed land development projects by Prime Lands Ltd across Kenya.'
    return render(request, template, ctx)


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    og_image = project.image.url if project.image else None
    template = 'projects/admin_project_detail.html' if request.user.is_authenticated and request.user.is_staff_or_above() else 'projects/project_detail.html'
    return render(request, template, {
        'project': project,
        'meta_description': f'{project.name} - {project.location}. {project.description|truncatewords:30 if project.description else f"{project.total_plots} plots available"}. View available plots at Prime Lands Ltd.',
        'og_title': f'{project.name} - Prime Lands Ltd',
        'og_description': f'{project.name} in {project.location}. {project.total_plots} plots available. Browse plots with flexible installment plans.',
        'og_type': 'product',
        'og_image': og_image,
        'structured_data': {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": project.name,
            "description": project.description or f"Land development project in {project.location}",
            "image": og_image,
            "brand": {
                "@type": "Organization",
                "name": "Prime Lands Ltd"
            }
        }
    })


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
