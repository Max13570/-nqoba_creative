from django.urls import path

from . import views

urlpatterns = [

    # Main website
    path('', views.home, name='home'),
    path('services/', views.services_page, name='services'),
    path('about/', views.about_page, name='about'),
    path('portfolio/', views.portfolio_page, name='portfolio'),
    path('contact/', views.contact_page, name='contact'),

    # Customer orders
    path('order/', views.place_order, name='place_order'),

    # Order tracking
    path('track-order/', views.track_order, name='track_order'),

    # Individual order details
    path(
        'track-order/<str:tracking_number>/',
        views.order_tracking,
        name='order_tracking'
    ),
]
