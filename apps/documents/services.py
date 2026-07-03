from .models import Document


def create_document(customer, doc_type, title, sale=None, file_content=None, uploaded_by=None, description='', is_auto=False):
    doc = Document(
        customer=customer,
        sale=sale,
        document_type=doc_type,
        title=title,
        description=description,
        uploaded_by=uploaded_by,
        is_auto_generated=is_auto,
    )
    if file_content:
        doc.file.save(file_content.name, file_content, save=False)
    doc.save()
    return doc


def replace_document(document, new_file, uploaded_by):
    document.status = 'replaced'
    document.save()
    new_doc = Document(
        customer=document.customer,
        sale=document.sale,
        document_type=document.document_type,
        title=document.title,
        description=document.description,
        uploaded_by=uploaded_by,
        version=document.version + 1,
    )
    new_doc.file.save(new_file.name, new_file, save=False)
    new_doc.save()
    return new_doc


def generate_auto_documents(sale):
    from apps.payments.models import Payment

    if sale.status == 'active' and not _has_document(sale, 'booking_form'):
        pass

    if sale.deposit_paid and not _has_document(sale, 'sale_agreement'):
        _create_simple_document(sale, 'sale_agreement', 'Sale Agreement')

    if sale.status == 'completed' and not _has_document(sale, 'completion_certificate'):
        _create_simple_document(sale, 'completion_certificate', 'Completion Certificate')


def _has_document(sale, doc_type):
    return Document.objects.filter(sale=sale, document_type=doc_type, status='active').exists()


def _create_simple_document(sale, doc_type, title):
    from django.core.files.base import ContentFile
    from django.template.loader import render_to_string
    from io import BytesIO
    from xhtml2pdf import pisa

    company_name = 'Prime Lands Ltd'
    try:
        from apps.settings.models import CompanySetting
        cs = CompanySetting.objects.first()
        if cs:
            company_name = cs.company_name
    except Exception:
        pass

    html = render_to_string(f'documents/auto_{doc_type}.html', {
        'sale': sale,
        'customer': sale.customer,
        'plot': sale.plot,
        'company_name': company_name,
    })
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result)
    if not pdf.err:
        filename = f'{doc_type}_{sale.id}.pdf'
        create_document(
            customer=sale.customer,
            doc_type=doc_type,
            title=title,
            sale=sale,
            file_content=ContentFile(result.getvalue(), name=filename),
            is_auto=True,
        )
