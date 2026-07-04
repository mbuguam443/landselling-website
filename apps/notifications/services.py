from .models import Notification


def create_notification(recipient, notification_type, title, message, link=''):
    Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link,
    )


def notify_payment(user, amount, receipt_number):
    create_notification(
        recipient=user,
        notification_type='payment',
        title='Payment Confirmed',
        message=f'Payment of KSh {amount:,.0f} (Receipt: {receipt_number}) has been confirmed.',
        link='/payments/',
    )


def notify_staff_payment(amount, receipt_number, customer_name):
    from apps.accounts.models import User
    staff_users = User.objects.exclude(role='customer')
    for staff in staff_users:
        create_notification(
            recipient=staff,
            notification_type='payment',
            title='Payment Received',
            message=f'{customer_name} paid KSh {amount:,.0f} (Receipt: {receipt_number}).',
            link='/payments/',
        )


def notify_staff_verification_ready(customer_name, customer_id):
    from apps.accounts.models import User
    staff_users = User.objects.exclude(role='customer')
    for staff in staff_users:
        create_notification(
            recipient=staff,
            notification_type='support',
            title='Verification Request',
            message=f'{customer_name} completed their profile and is ready for verification.',
            link=f'/customers/{customer_id}/',
        )


def notify_sale(user, plot_number):
    create_notification(
        recipient=user,
        notification_type='sale',
        title='Plot Allocated',
        message=f'Plot {plot_number} has been allocated to you.',
        link='/sales/',
    )


def notify_document(user, document_title):
    create_notification(
        recipient=user,
        notification_type='document',
        title='New Document',
        message=f'A new document "{document_title}" has been uploaded.',
        link='/documents/',
    )


def notify_reminder(user, message):
    create_notification(
        recipient=user,
        notification_type='reminder',
        title='Reminder',
        message=message,
    )


def notify_staff_new_customer(customer_name, customer_id):
    from apps.accounts.models import User
    staff_users = User.objects.exclude(role='customer')
    for staff in staff_users:
        create_notification(
            recipient=staff,
            notification_type='customer',
            title='New Customer Registered',
            message=f'{customer_name} has registered on the platform.',
            link=f'/customers/{customer_id}/',
        )
