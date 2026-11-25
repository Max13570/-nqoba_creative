from django.conf import settings


def site_info(request):
    """Business details available in every template."""
    return {
        'COMPANY_NAME': settings.COMPANY_NAME,
        'COMPANY_TAGLINE': settings.COMPANY_TAGLINE,
        'CURRENCY': settings.CURRENCY,
        'WHATSAPP_NUMBER': settings.WHATSAPP_NUMBER,
        'CONTACT_EMAIL': settings.CONTACT_EMAIL,
        'CONTACT_PHONES': settings.CONTACT_PHONES,
    }
