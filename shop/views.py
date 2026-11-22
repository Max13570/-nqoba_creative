from django.shortcuts import render
from .models import Service

def home(request):
    services = Service.objects.all()
    return render(request, 'shop/home.html', {'services': services})

def services_page(request):
    services = Service.objects.all()
    return render(request, 'shop/services.html', {'services': services})

def about_page(request):
    return render(request, 'shop/about.html')

def portfolio_page(request):
    services = Service.objects.all()
    return render(request, 'shop/portfolio.html', {'services': services})

def contact_page(request):
    return render(request, 'shop/contact.html')