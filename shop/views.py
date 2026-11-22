
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from .models import Service, Order


# =========================
# HOME PAGE
# =========================

def home(request):
    services = Service.objects.all()[:6]

    return render(request, 'shop/home.html', {
        'services': services
    })


# =========================
# SERVICES PAGE
# =========================

def services_page(request):
    services = Service.objects.all()

    return render(request, 'shop/services.html', {
        'services': services
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
    services = Service.objects.all()

    return render(request, 'shop/portfolio.html', {
        'services': services
    })


# =========================
# CONTACT PAGE
# =========================

def contact_page(request):
    return render(request, 'shop/contact.html')


# =========================
# CUSTOMER ORDER FORM
# =========================

def place_order(request):

    services = Service.objects.all()

    if request.method == 'POST':

        customer_name = request.POST.get('customer_name', '').strip()
        whatsapp = request.POST.get('whatsapp', '').strip()
        email = request.POST.get('email', '').strip()
        service_id = request.POST.get('service')
        details = request.POST.get('details', '').strip()
        quantity = request.POST.get('quantity', 1)
        deadline = request.POST.get('deadline')

        # Validate required fields
        if not all([
            customer_name,
            whatsapp,
            email,
            service_id,
            details,
            deadline
        ]):
            messages.error(
                request,
                'Please complete all required fields.'
            )

            return render(request, 'shop/order_form.html', {
                'services': services
            })

        # Validate service
        service = get_object_or_404(
            Service,
            id=service_id
        )

        # Validate quantity
        try:
            quantity = int(quantity)

            if quantity < 1:
                raise ValueError

        except (ValueError, TypeError):
            messages.error(
                request,
                'Please enter a valid quantity.'
            )

            return render(request, 'shop/order_form.html', {
                'services': services
            })

        # Validate deadline
        try:
            deadline_date = timezone.datetime.strptime(
                deadline,
                '%Y-%m-%d'
            ).date()

            if deadline_date < timezone.localdate():
                messages.error(
                    request,
                    'The deadline cannot be in the past.'
                )

                return render(request, 'shop/order_form.html', {
                    'services': services
                })

        except ValueError:
            messages.error(
                request,
                'Please select a valid deadline.'
            )

            return render(request, 'shop/order_form.html', {
                'services': services
            })

        # Create order
        order = Order.objects.create(
            customer_name=customer_name,
            whatsapp=whatsapp,
            email=email,
            service=service,
            details=details,
            quantity=quantity,
            deadline=deadline_date,
            status='NEW',
            quoted_price=service.price * quantity,
            amount_paid=0
        )

        messages.success(
            request,
            'Your order has been successfully submitted!'
        )

        return redirect(
            'order_tracking',
            tracking_number=order.tracking_number
        )

    return render(request, 'shop/order_form.html', {
        'services': services
    })


# =========================
# TRACK ORDER SEARCH
# =========================

def track_order(request):

    order = None
    tracking_number = ''

    if request.method == 'POST':

        tracking_number = request.POST.get(
            'tracking_number',
            ''
        ).strip().upper()

        if tracking_number:

            order = Order.objects.filter(
                tracking_number=tracking_number
            ).first()

            if not order:
                messages.error(
                    request,
                    'No order was found with that tracking number.'
                )

        else:
            messages.error(
                request,
                'Please enter your tracking number.'
            )

    return render(request, 'shop/track_order.html', {
        'order': order,
        'tracking_number': tracking_number
    })


# =========================
# ORDER TRACKING DETAILS
# =========================

def order_tracking(request, tracking_number):

    order = get_object_or_404(
        Order,
        tracking_number=tracking_number.upper()
    )

    return render(request, 'shop/order_details.html', {
        'order': order
    })
