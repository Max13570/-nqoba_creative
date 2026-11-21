from django.contrib import admin
from django.utils.html import format_html
from .models import Service, Order

# NQOBA CREATIVE Branding
admin.site.site_header = "NQOBA CREATIVE Admin"
admin.site.site_title = "Nqoba Creative"
admin.site.index_title = "Welcome to Nqoba Creative Dashboard"

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('image_thumb', 'name', 'price', 'delivery_days')
    list_display_links = ('name',)
    list_filter = ('delivery_days',)
    search_fields = ('name', 'description')
    list_editable = ('price', 'delivery_days')
    list_per_page = 20
    ordering = ('-id',)

    def image_thumb(self, obj):
        if obj.image:
            url = obj.image.url
            # If Cloudinary - load tiny 60px version, not 13MB full image
            if 'cloudinary' in url and '/upload/' in url:
                url = url.replace('/upload/', '/upload/w_60,h_60,c_fill,q_auto,f_auto/')
            return format_html('<img src="{}" style="width:60px;height:60px;object-fit:cover;border-radius:8px;border:2px solid #d4af37;" loading="lazy" />', url)
        return "No Image"
    image_thumb.short_description = "Image"

    class Media:
        css = {
            'all': ('shop/admin_fix.css',)
        }

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'service', 'status', 'deadline', 'created_at')
    list_filter = ('status', 'service', 'deadline')
    search_fields = ('customer_name', 'whatsapp', 'email')
    list_editable = ('status',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 20
    ordering = ('-created_at',)