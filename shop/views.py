import time
from urllib.parse import quote

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import EnquiryForm, OrderForm
from .models import Order, Service
from .notifications import notify_new_enquiry, notify_new_order

# Tracking-number lookups: allow this many wrong guesses per window.
TRACK_MAX_FAILURES = 8
TRACK_WINDOW_SECONDS = 15 * 60


def _active_services():
    return Service.objects.filter(is_active=True)


# =========================
# HOME PAGE
# =========================

def home(request):
    return render(request, 'shop/home.html', {
        'services': _active_services()[:6]
    })


# =========================
# SERVICES PAGE
# =========================

def services_page(request):
    return render(request, 'shop/services.html', {
        'services': _active_services()
    })


# =========================
# ABOUT PAGE
# =========================

def about_page(request):
    return render(request, 'shop/about.html')


# =========================
# PORTFOLIO PAGE
# =========================

def portfolio_page(request):
    return render(request, 'shop/portfolio.html', {
        'services': _active_services()
    })


# =========================
# CONTACT PAGE
# =========================

def contact_page(request):

    if request.method == 'POST':

        form = EnquiryForm(request.POST)

        if form.is_valid():

            # Hidden "website" field is only filled in by spam bots.
            # Pretend it worked, but save nothing.
            if form.cleaned_data.get('website'):
                return redirect('contact')

            enquiry = form.save()
            notify_new_enquiry(enquiry)

            request.session['enquiry_whatsapp_text'] = (
                'NEW PROJECT ENQUIRY - NQOBA CREATIVE\n\n'
                f'Name: {enquiry.name}\n'
                f'Phone: {enquiry.phone}\n'
                f'Service: {enquiry.service}\n'
                f'Budget: {enquiry.budget or "Not specified"}\n\n'
                f'{enquiry.message}'
            )

            messages.success(
                request,
                'Thank you. Your enquiry has been received and we will '
                'contact you soon.'
            )

            return redirect('contact')

        for field_name, errors in form.errors.items():
            label = (
                form.fields[field_name].label
                or field_name.replace('_', ' ').title()
            ) if field_name in form.fields else 'Form'

            for error in errors:
                messages.error(request, f'{label}: {error}')

        return render(request, 'shop/contact.html')

    whatsapp_text = request.session.pop('enquiry_whatsapp_text', None)

    return render(request, 'shop/contact.html', {
        'whatsapp_text_encoded': quote(whatsapp_text) if whatsapp_text else '',
    })


# =========================
# CUSTOMER ORDER FORM
# =========================

def place_order(request):

    if request.method == 'POST':

        form = OrderForm(request.POST)

        if form.is_valid():

            if form.cleaned_data.get('website'):
                return redirect('home')

            order = form.save(commit=False)
            order.status = 'NEW'
            order.amount_paid = 0
            order.quoted_price = order.service.price * order.quantity
            order.save()

            tracking_url = request.build_absolute_uri(
                reverse('order_tracking', args=[order.tracking_number])
            )

            notify_new_order(order, tracking_url)

            messages.success(
                request,
                'Your order has been submitted. Save your tracking number '
                'below so you can follow its progress.'
            )

            return redirect(
                'order_tracking',
                tracking_number=order.tracking_number
            )

    else:
        initial = {}
        service_id = request.GET.get('service', '')

        if service_id.isdigit():
            initial['service'] = int(service_id)

        form = OrderForm(initial=initial)

    return render(request, 'shop/order_form.html', {
        'form': form,
    })


# =========================
# TRACK ORDER SEARCH
# =========================

def _recent_failures(request):
    now = time.time()
    failures = [
        stamp for stamp in request.session.get('track_failures', [])
        if now - stamp < TRACK_WINDOW_SECONDS
    ]
    request.session['track_failures'] = failures
    return failures


def _normalise_tracking_number(raw):
    value = (raw or '').strip().upper().replace(' ', '')

    # Allow customers to type only the 8 characters after "NQ-"
    if len(value) == 8 and not value.startswith('NQ'):
        value = f'NQ-{value}'

    return value


def track_order(request):

    order = None
    tracking_number = ''

    if request.method == 'POST':

        tracking_number = _normalise_tracking_number(
            request.POST.get('tracking_number')
        )

        failures = _recent_failures(request)

        if len(failures) >= TRACK_MAX_FAILURES:
            messages.error(
                request,
                'Too many unsuccessful attempts. Please wait a few '
                'minutes and try again.'
            )

        elif not tracking_number:
            messages.error(request, 'Please enter your tracking number.')

        else:
            order = Order.objects.filter(
                tracking_number=tracking_number
            ).select_related('service').first()

            if not order:
                failures.append(time.time())
                request.session['track_failures'] = failures

                messages.error(
                    request,
                    'No order was found with that tracking number. '
                    'Check it and try again.'
                )

    return render(request, 'shop/track_order.html', {
        'order': order,
        'tracking_number': tracking_number,
    })


# =========================
# ORDER TRACKING DETAILS
# =========================

def order_tracking(request, tracking_number):

    order = get_object_or_404(
        Order.objects.select_related('service'),
        tracking_number=tracking_number.upper()
    )

    return render(request, 'shop/order_details.html', {
        'order': order
    })
