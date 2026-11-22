
from django.db import models
from django.utils import timezone
import secrets


# ==========================================
# TRACKING NUMBER GENERATOR
# ==========================================

def generate_tracking_number():
    """
    Generate a unique tracking number.

    Format:
    NQ-XXXXXXXX
    """

    return f"NQ-{secrets.token_hex(4).upper()}"


# ==========================================
# SERVICE MODEL
# ==========================================

class Service(models.Model):

    name = models.CharField(
        max_length=100
    )

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    description = models.TextField()

    delivery_days = models.IntegerField(
        default=3
    )

    image = models.ImageField(
        upload_to='services/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


# ==========================================
# ORDER MODEL
# ==========================================

class Order(models.Model):

    # ==========================================
    # ORDER STATUS
    # ==========================================

    STATUS_CHOICES = [

        ('NEW', 'Order Received'),

        ('CONFIRMED', 'Confirmed'),

        ('IN_PROGRESS', 'Design In Progress'),

        ('REVIEW', 'Awaiting Client Review'),

        ('REVISION', 'Revision In Progress'),

        ('DONE', 'Completed'),

        ('DELIVERED', 'Delivered'),

        ('CANCELLED', 'Cancelled'),

    ]

    # ==========================================
    # PAYMENT STATUS
    # ==========================================

    PAYMENT_STATUS_CHOICES = [

        ('UNPAID', 'Unpaid'),

        ('PARTIAL', 'Partially Paid'),

        ('PAID', 'Fully Paid'),

    ]

    # ==========================================
    # ORDER IDENTIFICATION
    # ==========================================

    tracking_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        editable=False,
        db_index=True
    )

    # ==========================================
    # CUSTOMER INFORMATION
    # ==========================================

    customer_name = models.CharField(
        max_length=100
    )

    whatsapp = models.CharField(
        max_length=20
    )

    email = models.EmailField()

    # ==========================================
    # ORDER INFORMATION
    # ==========================================

    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name='orders'
    )

    details = models.TextField()

    quantity = models.PositiveIntegerField(
        default=1
    )

    deadline = models.DateField()

    # ==========================================
    # ORDER STATUS
    # ==========================================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='NEW',
        db_index=True
    )

    progress_note = models.TextField(
        blank=True,
        default=''
    )

    # ==========================================
    # PAYMENT INFORMATION
    # ==========================================

    quoted_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='UNPAID',
        db_index=True
    )

    # ==========================================
    # ORDER DATES
    # ==========================================

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    completed_at = models.DateTimeField(
        blank=True,
        null=True
    )

    # ==========================================
    # BALANCE PROPERTY
    # ==========================================

    @property
    def balance(self):
        """
        Calculate the remaining payment balance.
        """

        return max(
            self.quoted_price - self.amount_paid,
            0
        )

    # ==========================================
    # PROGRESS PROPERTY
    # ==========================================

    @property
    def progress_percentage(self):
        """
        Calculate progress based on order status.
        """

        progress_values = {

            'NEW': 10,

            'CONFIRMED': 20,

            'IN_PROGRESS': 50,

            'REVIEW': 75,

            'REVISION': 85,

            'DONE': 95,

            'DELIVERED': 100,

            'CANCELLED': 0,

        }

        return progress_values.get(
            self.status,
            0
        )

    # ==========================================
    # COMPLETION PROPERTY
    # ==========================================

    @property
    def is_completed(self):

        return self.status in [
            'DONE',
            'DELIVERED'
        ]

    # ==========================================
    # SAVE METHOD
    # ==========================================

    def save(self, *args, **kwargs):

        # Generate tracking number if missing
        if not self.tracking_number:

            while True:

                tracking_number = generate_tracking_number()

                if not Order.objects.filter(
                    tracking_number=tracking_number
                ).exists():

                    self.tracking_number = tracking_number

                    break

        # Automatically update completion date
        if self.status in ['DONE', 'DELIVERED']:

            if not self.completed_at:

                self.completed_at = timezone.now()

        else:

            self.completed_at = None

        # Automatically calculate payment status
        if self.quoted_price > 0:

            if self.amount_paid >= self.quoted_price:

                self.payment_status = 'PAID'

            elif self.amount_paid > 0:

                self.payment_status = 'PARTIAL'

            else:

                self.payment_status = 'UNPAID'

        super().save(*args, **kwargs)

    # ==========================================
    # STRING REPRESENTATION
    # ==========================================

    def __str__(self):

        return (
            f"{self.tracking_number} - "
            f"{self.customer_name} - "
            f"{self.service.name}"
        )

    # ==========================================
    # MODEL SETTINGS
    # ==========================================

    class Meta:

        ordering = ['-created_at']

        verbose_name = 'Customer Order'

        verbose_name_plural = 'Customer Orders'
