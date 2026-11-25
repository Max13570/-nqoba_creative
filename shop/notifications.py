"""
Email notifications. Every function swallows errors so that a mail problem
can never stop a customer from placing an order or sending an enquiry.
"""

import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def _send(subject, body, recipients):
    recipients = [address for address in recipients if address]

    if not recipients:
        return False

    try:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            recipients,
            fail_silently=False,
        )
        return True
    except Exception:
        logger.exception('Could not send email "%s"', subject)
        return False


def notify_new_order(order, tracking_url):
    """Alert the owner and confirm to the customer."""

    _send(
        f'New order {order.tracking_number} - {order.service.name}',
        (
            f'A new order has been placed.\n\n'
            f'Tracking number: {order.tracking_number}\n'
            f'Customer: {order.customer_name}\n'
            f'WhatsApp: {order.whatsapp}\n'
            f'Email: {order.email}\n'
            f'Service: {order.service.name}\n'
            f'Quantity: {order.quantity}\n'
            f'Deadline: {order.deadline:%d %b %Y}\n'
            f'Estimated price: {settings.CURRENCY}{order.quoted_price:,.2f}\n\n'
            f'Details:\n{order.details}\n'
        ),
        [settings.ORDER_NOTIFY_EMAIL],
    )

    _send(
        f'We received your order {order.tracking_number}',
        (
            f'Hi {order.customer_name},\n\n'
            f'Thank you for your order with {settings.COMPANY_NAME}.\n\n'
            f'Your tracking number is {order.tracking_number}.\n'
            f'Follow your order here: {tracking_url}\n\n'
            f'We will review your requirements and confirm your final price '
            f'shortly. You can also reach us on WhatsApp: '
            f'+{settings.WHATSAPP_NUMBER}.\n\n'
            f'{settings.COMPANY_NAME} - {settings.COMPANY_TAGLINE}\n'
        ),
        [order.email],
    )


def notify_status_change(order, tracking_url):
    """Tell the customer their order moved to a new stage."""

    _send(
        f'Order {order.tracking_number}: {order.get_status_display()}',
        (
            f'Hi {order.customer_name},\n\n'
            f'Your order {order.tracking_number} ({order.service.name}) is now: '
            f'{order.get_status_display()}.\n\n'
            + (f'Update from our team:\n{order.progress_note}\n\n' if order.progress_note else '')
            + f'Follow your order here: {tracking_url}\n\n'
            f'{settings.COMPANY_NAME} - {settings.COMPANY_TAGLINE}\n'
        ),
        [order.email],
    )


def notify_new_enquiry(enquiry):
    """Alert the owner about a new project enquiry."""

    _send(
        f'New enquiry from {enquiry.name} - {enquiry.service}',
        (
            f'A new project enquiry was sent from the website.\n\n'
            f'Name: {enquiry.name}\n'
            f'Email: {enquiry.email}\n'
            f'Phone: {enquiry.phone}\n'
            f'Service: {enquiry.service}\n'
            f'Budget: {enquiry.budget or "Not specified"}\n\n'
            f'Message:\n{enquiry.message}\n'
        ),
        [settings.ORDER_NOTIFY_EMAIL],
    )
