from datetime import date
from django.utils import timezone
from .models import InstallmentSchedule


def check_overdue_installments(sale=None):
    today = timezone.now().date()
    qs = InstallmentSchedule.objects.filter(due_date__lt=today, status__in=['pending', 'partially_paid'])
    if sale:
        qs = qs.filter(sale=sale)
    count = 0
    for inst in qs:
        if inst.is_overdue:
            inst.status = 'overdue'
            inst.save()
            count += 1
    return count


def get_overdue_summary():
    from django.db.models import Sum, Count, Q, F
    from .models import Sale

    overdue_inst = InstallmentSchedule.objects.filter(
        status='overdue'
    ).aggregate(
        total_count=Count('id'),
        total_amount=Sum(F('amount') - F('amount_paid'))
    )

    return {
        'overdue_count': overdue_inst['total_count'] or 0,
        'overdue_amount': overdue_inst['total_amount'] or 0,
    }
