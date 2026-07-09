from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.decorators import staff_required
from apps.notifications.services import notify_document
from .models import Document


@login_required
def document_list(request):
    from apps.core.utils import get_sortable_context
    if request.user.is_staff_or_above() or request.user.is_superuser:
        documents = Document.objects.select_related('customer__user', 'uploaded_by').all()
        template = 'documents/document_list.html'
    else:
        documents = Document.objects.filter(customer__user=request.user).select_related('uploaded_by')
        template = 'documents/customer_document_list.html'
    ctx = get_sortable_context(request, documents, default_sort='-created_at',
                               allowed_fields=['title', 'document_type', 'status', 'created_at'],
                               search_fields=['title', 'document_type', 'customer__name'],
                               per_page=15)
    ctx['is_staff'] = request.user.is_staff_or_above() or request.user.is_superuser
    return render(request, template, ctx)


@login_required
@staff_required
def document_upload(request):
    if request.method == 'POST':
        from .forms import DocumentForm
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.uploaded_by = request.user
            doc.save()
            notify_document(doc.customer.user, doc.title)
            messages.success(request, 'Document uploaded successfully.')
            return redirect('documents:document_list')
    else:
        from .forms import DocumentForm
        form = DocumentForm()
    return render(request, 'documents/document_form.html', {'form': form, 'title': 'Upload Document'})


@login_required
def document_detail(request, pk):
    doc = get_object_or_404(Document.objects.select_related('customer__user', 'uploaded_by'), pk=pk)
    if not (request.user.is_staff_or_above() or request.user.is_superuser) and doc.customer.user != request.user:
        messages.error(request, 'You do not have access to this document.')
        return redirect('dashboard:home')
    template = 'documents/document_detail.html' if request.user.is_staff_or_above() or request.user.is_superuser else 'documents/customer_document_detail.html'
    return render(request, template, {'doc': doc, 'is_staff': request.user.is_staff_or_above() or request.user.is_superuser})
