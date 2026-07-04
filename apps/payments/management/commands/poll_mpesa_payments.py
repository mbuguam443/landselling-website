import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.payments.models import Payment, MpesaTransaction
from apps.payments.mpesa import query_stk_status
from apps.payments.services import process_payment

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Poll Safaricom for pending M-Pesa payments and auto-confirm them'

    def handle(self, *args, **options):
        cutoff = timezone.now() - timezone.timedelta(minutes=5)
        pending_txns = MpesaTransaction.objects.filter(
            status='pending',
            transaction_type='stk_push',
            created_at__gte=cutoff,
        ).select_related('payment')

        if not pending_txns.exists():
            self.stdout.write(self.style.SUCCESS('No pending M-Pesa transactions to check.'))
            return

        confirmed = 0
        for txn in pending_txns:
            payment = txn.payment
            if payment.status in ('completed', 'confirmed'):
                txn.status = 'success'
                txn.save()
                continue

            if not txn.checkout_request_id:
                continue

            self.stdout.write(f'Querying Safaricom for {txn.checkout_request_id}...')
            response_data = query_stk_status(txn.checkout_request_id)
            result_code = response_data.get('ResultCode', '1')

            if result_code == '0':
                receipt = response_data.get('Receipt', '') or response_data.get('MpesaReceiptNumber', '')
                if not receipt:
                    receipt = 'QRY' + timezone.now().strftime('%y%m%d%H%M%S')

                txn.result_code = result_code
                txn.result_description = response_data.get('ResultDesc', 'Success')
                txn.mpesa_receipt_number = receipt
                txn.transaction_date = timezone.now()
                txn.raw_callback_data = response_data
                txn.status = 'success'
                txn.save()

                payment.transaction_code = receipt
                payment.mpesa_code = receipt
                payment.status = 'pending'
                payment.save()

                process_payment(payment)
                confirmed += 1
                self.stdout.write(self.style.SUCCESS(f'Confirmed payment #{payment.pk} - KSh {payment.amount}'))
            else:
                desc = response_data.get('ResultDesc', 'Still pending')
                self.stdout.write(f'  Not yet: {desc}')

        self.stdout.write(self.style.SUCCESS(f'Done. Confirmed {confirmed} payment(s).'))
