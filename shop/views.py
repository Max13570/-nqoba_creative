from django.shortcuts import render, redirect
from .models import Service, Order

def home(request):
    services = Service.objects.all()
    if request.method == 'POST':
        Order.objects.create(
            customer_name=request.POST.get('name'),
            whatsapp=request.POST.get('whatsapp'),
            email=request.POST.get('email'),
            service_id=request.POST.get('service'),
            details=request.POST.get('details'),
            deadline=request.POST.get('deadline'),
        )
        return redirect('/?success=1')
    return render(request, 'shop/home.html', {'services': services})