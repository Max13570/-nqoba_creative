from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html

from .models import Enquiry, Order, Service
from .notifications import notify_status_change


# =========================================================
# NQOBA CREATIVE ADMIN BRANDING
# =========================================================

admin.site.site_header = "NQOBA CREATIVE"
admin.site.site_title = "Nqoba Creative Admin"
admin.site.index_title = "Business Management Dashboard"


# =========================================================
# SERVICE ADMIN
# =========================================================

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):

    list_display = (
        'image_thumb',
        'name',
        'price_display',
        'delivery_days',
        'is_active',
        'created_at',
    )

    list_display_links = ('name',)

    list_filter = ('is_active', 'delivery_days', 'created_at')

    search_fields = ('name', 'description')

    list_editable = ('delivery_days', 'is_active')

    list_per_page = 20

    ordering = ('-id',)

    readonly_fields = ('image_preview', 'created_at')

    fieldsets = (
        (
            'Service Information',
            {
                'fields': (
                    'name',
                    'description',
                    'price',
                    'delivery_days',
                    'is_active',
                )
            }
        ),
        (
            'Service Image',
            {'fields': ('image', 'image_preview')}
        ),
        (
            'System Information',
            {
                'fields': ('created_at',),
                'classes': ('collapse',),
            }
        ),
    )

    @admin.display(description='Image')
    def image_thumb(self, obj):

        if obj.image:

            image_url = obj.image.url

            if 'cloudinary' in image_url and '/upload/' in image_url:
                image_url = image_url.replace(
                    '/upload/',
                    '/upload/w_80,h_80,c_fill,q_auto,f_auto/'
                )

            return format_html(
                '<img src="{}" width="60" height="60" loading="lazy" '
                'style="object-fit:cover;border-radius:10px;'
                'border:2px solid #d4af37;" />',
                image_url
            )

        return format_html('<span style="color:#999;">No Image</span>')

    @admin.display(description='Price', ordering='price')
    def price_display(self, obj):
        return format_html(
            '<strong style="color:#123b2a;">E{}</strong>',
            f'{obj.price:,.2f}'
        )

    @admin.display(description='Image Preview')
    def image_preview(self, obj):

        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:350px;max-height:250px;'
                'object-fit:contain;border-radius:12px;'
                'border:2px solid #d4af37;padding:5px;background:white;" />',
                obj.image.url
            )

        return "No image uploaded"


# =========================================================
# ORDER ADMIN
# =========================================================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'tracking_number',
        'customer_name',
        'service',
        'status_badge',
        'payment_badge',
        'quoted_price_display',
        'amount_paid_display',
        'balance_display',
        'deadline',
        'whatsapp_chat',
        'created_at',
    )

    list_display_links = ('tracking_number', 'customer_name')

    list_filter = (
        'status',
        'payment_status',
        'service',
        'deadline',
        'created_at',
    )

    search_fields = (
        'tracking_number',
        'customer_name',
        'whatsapp',
        'email',
        'service__name',
    )

    list_select_related = ('service',)

    list_per_page = 25

    ordering = ('-created_at',)

    date_hierarchy = 'created_at'

    readonly_fields = (
        'tracking_number',
        'created_at',
        'updated_at',
        'completed_at',
        'payment_status',
        'balance_display',
        'progress_display',
    )

    fieldsets = (
        (
            'Order Information',
            {
                'fields': (
                    'tracking_number',
                    'customer_name',
                    'whatsapp',
                    'email',
                    'service',
                    'details',
                    'quantity',
                    'deadline',
                )
            }
        ),
        (
            'Order Progress',
            {
                'description': (
                    'Changing the status emails the customer automatically '
                    'when email is configured.'
                ),
                'fields': (
                    'status',
                    'progress_note',
                    'progress_display',
                )
            }
        ),
        (
            'Payment Information',
            {
                'fields': (
                    'quoted_price',
                    'amount_paid',
                    'payment_status',
                    'balance_display',
                )
            }
        ),
        (
            'System Information',
            {
                'fields': ('created_at', 'updated_at', 'completed_at'),
                'classes': ('collapse',),
            }
        ),
    )

    actions = (
        'mark_confirmed',
        'mark_in_progress',
        'mark_review',
        'mark_revision',
        'mark_done',
        'mark_delivered',
        'mark_cancelled',
    )

    # -----------------------------------------------------
    # Email the customer when the status changes in the form
    # -----------------------------------------------------

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if change and 'status' in form.changed_data:
            self._notify_customer(request, obj)

    def _notify_customer(self, request, order):
        tracking_url = request.build_absolute_uri(
            reverse('order_tracking', args=[order.tracking_number])
        )
        notify_status_change(order, tracking_url)

    # -----------------------------------------------------
    # Display columns
    # -----------------------------------------------------

    @admin.display(description='Order Status', ordering='status')
    def status_badge(self, obj):

        colors = {
            'NEW': '#2563eb',
            'CONFIRMED': '#7c3aed',
            'IN_PROGRESS': '#d97706',
            'REVIEW': '#0891b2',
            'REVISION': '#dc2626',
            'DONE': '#16a34a',
            'DELIVERED': '#15803d',
            'CANCELLED': '#6b7280',
        }

        return format_html(
            '<span style="background:{};color:white;padding:5px 10px;'
            'border-radius:20px;font-size:11px;font-weight:bold;'
            'white-space:nowrap;">{}</span>',
            colors.get(obj.status, '#64748b'),
            obj.get_status_display()
        )

    @admin.display(description='Payment', ordering='payment_status')
    def payment_badge(self, obj):

        colors = {
            'UNPAID': '#dc2626',
            'PARTIAL': '#d97706',
            'PAID': '#16a34a',
        }

        return format_html(
            '<span style="background:{};color:white;padding:5px 10px;'
            'border-radius:20px;font-size:11px;font-weight:bold;'
            'white-space:nowrap;">{}</span>',
            colors.get(obj.payment_status, '#64748b'),
            obj.get_payment_status_display()
        )

    @admin.display(description='Quoted Price', ordering='quoted_price')
    def quoted_price_display(self, obj):

        if obj.quoted_price is None:
            return format_html('<span style="color:#999;">Not quoted</span>')

        return format_html(
            '<strong>E{}</strong>',
            f'{obj.quoted_price:,.2f}'
        )

    @admin.display(description='Amount Paid', ordering='amount_paid')
    def amount_paid_display(self, obj):
        return format_html(
            '<span style="color:#16a34a;font-weight:bold;">E{}</span>',
            f'{obj.amount_paid:,.2f}'
        )

    @admin.display(description='Balance')
    def balance_display(self, obj):

        balance = obj.balance
        color = '#16a34a' if balance <= 0 else '#dc2626'

        return format_html(
            '<strong style="color:{};">E{}</strong>',
            color,
            f'{balance:,.2f}'
        )

    @admin.display(description='Chat')
    def whatsapp_chat(self, obj):

        if not obj.whatsapp_digits:
            return '-'

        return format_html(
            '<a href="https://wa.me/{}" target="_blank" '
            'rel="noopener noreferrer">WhatsApp</a>',
            obj.whatsapp_digits
        )

    @admin.display(description='Progress')
    def progress_display(self, obj):

        progress = obj.progress_percentage

        return format_html(
            '<div style="width:250px;background:#e5e7eb;'
            'border-radius:20px;overflow:hidden;height:18px;">'
            '<div style="width:{}%;background:#123b2a;height:18px;'
            'border-radius:20px;"></div></div>'
            '<span style="font-weight:bold;color:#123b2a;margin-top:5px;'
            'display:inline-block;">{}%</span>',
            progress,
            progress
        )

    # -----------------------------------------------------
    # Bulk actions
    #
    # These call save() on every order (not queryset.update) so that
    # completed_at and payment_status stay correct and the customer is
    # emailed about the change.
    # -----------------------------------------------------

    def _bulk_set_status(self, request, queryset, status, label):

        changed = 0

        for order in queryset.select_related('service'):

            if order.status == status:
                continue

            order.status = status
            order.save()
            self._notify_customer(request, order)
            changed += 1

        self.message_user(
            request,
            f'{changed} order(s) marked as {label}.',
            messages.SUCCESS
        )

    @admin.action(description='Mark selected orders as Confirmed')
    def mark_confirmed(self, request, queryset):
        self._bulk_set_status(request, queryset, 'CONFIRMED', 'Confirmed')

    @admin.action(description='Mark selected orders as In Progress')
    def mark_in_progress(self, request, queryset):
        self._bulk_set_status(request, queryset, 'IN_PROGRESS', 'In Progress')

    @admin.action(description='Mark selected orders as Ready for Review')
    def mark_review(self, request, queryset):
        self._bulk_set_status(request, queryset, 'REVIEW', 'Ready for Review')

    @admin.action(description='Mark selected orders as Revision')
    def mark_revision(self, request, queryset):
        self._bulk_set_status(request, queryset, 'REVISION', 'Revision')

    @admin.action(description='Mark selected orders as Completed')
    def mark_done(self, request, queryset):
        self._bulk_set_status(request, queryset, 'DONE', 'Completed')

    @admin.action(description='Mark selected orders as Delivered')
    def mark_delivered(self, request, queryset):
        self._bulk_set_status(request, queryset, 'DELIVERED', 'Delivered')

    @admin.action(description='Mark selected orders as Cancelled')
    def mark_cancelled(self, request, queryset):
        self._bulk_set_status(request, queryset, 'CANCELLED', 'Cancelled')


# =========================================================
# ENQUIRY ADMIN
# =========================================================

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'service',
        'phone',
        'email',
        'budget',
        'is_read',
        'created_at',
    )

    list_filter = ('is_read', 'service', 'created_at')

    search_fields = ('name', 'email', 'phone', 'service', 'message')

    list_editable = ('is_read',)

    list_per_page = 25

    date_hierarchy = 'created_at'

    readonly_fields = (
        'name',
        'email',
        'phone',
        'service',
        'budget',
        'message',
        'created_at',
    )

    fields = readonly_fields + ('is_read',)

    actions = ('mark_read',)

    def has_add_permission(self, request):
        # Enquiries come from the website contact form only.
        return False

    @admin.action(description='Mark selected enquiries as read')
    def mark_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(
            request,
            f'{updated} enquiry(ies) marked as read.',
            messages.SUCCESS
        )
