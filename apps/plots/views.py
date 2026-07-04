from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.decorators import staff_required
from apps.reports.utils import log_audit
from .models import Plot, PlotImage
from .forms import PlotForm, PlotFilterForm, PlotImageFormSet


def plot_list(request):
    from apps.core.utils import get_sortable_context
    plots = Plot.objects.select_related('project', 'phase').prefetch_related('images', 'amenities')
    is_staff_user = request.user.is_authenticated and request.user.is_staff_or_above()
    if not is_staff_user:
        plots = plots.filter(status='available')
    plots = plots.all()
    form = PlotFilterForm(request.GET or None)
    if form.is_valid():
        if form.cleaned_data.get('project'):
            plots = plots.filter(project_id=form.cleaned_data['project'])
        if form.cleaned_data.get('min_price'):
            plots = plots.filter(price__gte=form.cleaned_data['min_price'])
        if form.cleaned_data.get('max_price'):
            plots = plots.filter(price__lte=form.cleaned_data['max_price'])
        if form.cleaned_data.get('min_size'):
            plots = plots.filter(size_sqm__gte=form.cleaned_data['min_size'])
        if form.cleaned_data.get('max_size'):
            plots = plots.filter(size_sqm__lte=form.cleaned_data['max_size'])
        if form.cleaned_data.get('status'):
            plots = plots.filter(status=form.cleaned_data['status'])
    ctx = get_sortable_context(request, plots, default_sort='plot_number',
                               allowed_fields=['plot_number', 'size_sqm', 'price', 'status'],
                               search_fields=['plot_number', 'project__name', 'project__location'],
                               per_page=12)
    ctx['form'] = form
    breadcrumbs = [
        {'label': 'Home', 'url': '/'},
        {'label': 'Plots', 'url': ''},
    ]
    ctx['breadcrumbs'] = breadcrumbs
    ctx['meta_description'] = 'Browse available plots for sale in Kenya. Find prime land in Nairobi and surrounding areas with flexible installment plans at Prime Lands Ltd.'
    ctx['og_title'] = 'Available Plots for Sale - Prime Lands Ltd'
    ctx['og_description'] = 'Explore verified plots for sale in Kenya. Affordable land with guaranteed title deeds and flexible payment plans.'
    template = 'plots/admin_plot_list.html' if request.user.is_authenticated and request.user.is_staff_or_above() else 'plots/plot_list.html'
    return render(request, template, ctx)


def plot_detail(request, pk):
    plot = get_object_or_404(
        Plot.objects.select_related('project', 'phase').prefetch_related('images', 'amenities'),
        pk=pk
    )
    is_staff_user = request.user.is_authenticated and request.user.is_staff_or_above()
    if not is_staff_user and plot.status != 'available':
        messages.info(request, 'This plot is not available for viewing.')
        return redirect('plots:plot_list')
    breadcrumbs = [
        {'label': 'Home', 'url': '/'},
        {'label': 'Plots', 'url': '{% url "plots:plot_list" %}'},
        {'label': plot.plot_number, 'url': ''},
    ]
    map_embed_url = None
    if plot.project.coordinates:
        try:
            lat, lng = plot.project.coordinates.replace(' ', '').split(',')
            lat, lng = float(lat), float(lng)
            map_embed_url = f"https://www.openstreetmap.org/export/embed.html?bbox={lng-0.01},{lat-0.01},{lng+0.01},{lat+0.01}&layer=mapnik&marker={lat},{lng}"
        except (ValueError, AttributeError):
            pass

    plot_image = plot.images.first()
    og_image = plot_image.image.url if plot_image else None

    template = 'plots/admin_plot_detail.html' if request.user.is_authenticated and request.user.is_staff_or_above() else 'plots/plot_detail.html'
    return render(request, template, {
        'plot': plot,
        'breadcrumbs': breadcrumbs,
        'map_embed_url': map_embed_url,
        'meta_description': f'Plot {plot.plot_number} in {plot.project.name}, {plot.project.location} - {plot.size_sqm} sqm at KSh {plot.price:,.0f}. {plot.get_status_display()} with flexible installment plans at Prime Lands Ltd.',
        'og_title': f'Plot {plot.plot_number} - {plot.project.name} | Prime Lands Ltd',
        'og_description': f'{plot.size_sqm} sqm plot in {plot.project.name}, {plot.project.location}. Price: KSh {plot.price:,.0f}. Status: {plot.get_status_display()}.',
        'og_type': 'product',
        'og_image': og_image,
        'structured_data': {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": f"Plot {plot.plot_number} - {plot.project.name}",
            "description": f"{plot.size_sqm} sqm plot in {plot.project.name}, {plot.project.location}",
            "image": og_image,
            "offers": {
                "@type": "Offer",
                "price": str(plot.price),
                "priceCurrency": "KES",
                "availability": "https://schema.org/InStock" if plot.status == 'available' else "https://schema.org/OutOfOfStock",
            },
            "brand": {
                "@type": "Organization",
                "name": "Prime Lands Ltd"
            }
        }
    })


@login_required
@staff_required
def plot_create(request):
    form = PlotForm()
    formset = PlotImageFormSet()
    if request.method == 'POST':
        form = PlotForm(request.POST, request.FILES)
        if form.is_valid():
            plot = form.save()
            formset = PlotImageFormSet(request.POST, request.FILES, instance=plot)
            if formset.is_valid():
                formset.save()
            log_audit(request.user, 'create', model_name='Plot', object_id=plot.pk,
                      object_repr=plot.plot_number, description=f'Plot {plot.plot_number} created in {plot.project.name}', request=request)
            messages.success(request, 'Plot created successfully.')
            return redirect('plots:plot_detail', pk=plot.pk)
    return render(request, 'plots/plot_form.html', {'form': form, 'formset': formset, 'title': 'Create Plot'})


@login_required
@staff_required
def plot_edit(request, pk):
    plot = get_object_or_404(Plot, pk=pk)
    form = PlotForm(instance=plot)
    formset = PlotImageFormSet(instance=plot)
    if request.method == 'POST':
        form = PlotForm(request.POST, request.FILES, instance=plot)
        formset = PlotImageFormSet(request.POST, request.FILES, instance=plot)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Plot updated successfully.')
            return redirect('plots:plot_detail', pk=plot.pk)
    return render(request, 'plots/plot_form.html', {'form': form, 'formset': formset, 'title': 'Edit Plot'})


@login_required
@staff_required
def plot_delete(request, pk):
    plot = get_object_or_404(Plot, pk=pk)
    if request.method == 'POST':
        plot.delete()
        messages.success(request, 'Plot deleted successfully.')
        return redirect('plots:plot_list')
    return render(request, 'components/confirm_delete.html', {'object': plot})
