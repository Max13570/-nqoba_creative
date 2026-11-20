from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField()
    delivery_days = models.IntegerField(default=3)
    image = models.ImageField(upload_to='services/', blank=True, null=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'New Order'),
        ('IN_PROGRESS', 'In Progress'),
        ('DONE', 'Done'),
        ('DELIVERED', 'Delivered'),
    ]
    customer_name = models.CharField(max_length=100)
    whatsapp = models.CharField(max_length=20)
    email = models.EmailField()
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    details = models.TextField()
    deadline = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.service.name}"