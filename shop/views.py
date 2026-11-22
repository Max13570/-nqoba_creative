from django.shortcuts import render
from .models import Service

def home(request):
    services = Service.objects.all()
    return render(request, 'home.html', {'services': services})

def services_page(request):
    services = Service.objects.all()
    return render(request, 'services.html', {'services': services})

def about_page(request):
    return render(request, 'about.html')

def portfolio_page(request):
    services = Service.objects.all()
    return render(request, 'portfolio.html', {'services': services})

def contact_page(request):
    return render(request, 'contact.html')