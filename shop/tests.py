from datetime import timedelta
from decimal import Decimal

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Enquiry, Order, Service


def make_service(**kwargs):
    defaults = {
        'name': 'Logo Design',
        'price': Decimal('370.00'),
        'description': 'A logo.',
        'delivery_days': 3,
    }
    defaults.update(kwargs)
    return Service.objects.create(**defaults)


def order_payload(service, **overrides):
    data = {
        'customer_name': 'Thandi Dlamini',
        'whatsapp': '+268 7833 6238',
        'email': 'thandi@example.com',
        'service': service.pk,
        'quantity': 2,
        'deadline': (timezone.localdate() + timedelta(days=7)).isoformat(),
        'details': 'Green and gold logo for a bakery.',
        'website': '',
    }
    data.update(overrides)
    return data


class OrderModelTests(TestCase):

    def setUp(self):
        self.service = make_service()

    def _order(self, **kwargs):
        defaults = {
            'customer_name': 'A',
            'whatsapp': '78336238',
            'email': 'a@example.com',
            'service': self.service,
            'details': 'details here',
            'deadline': timezone.localdate(),
            'quoted_price': Decimal('100'),
        }
        defaults.update(kwargs)
        return Order.objects.create(**defaults)

    def test_tracking_number_generated(self):
        order = self._order()
        self.assertRegex(order.tracking_number, r'^NQ-[0-9A-F]{8}$')

    def test_payment_status_follows_amounts(self):
        order = self._order()
        self.assertEqual(order.payment_status, 'UNPAID')

        order.amount_paid = Decimal('40')
        order.save()
        self.assertEqual(order.payment_status, 'PARTIAL')
        self.assertEqual(order.balance, Decimal('60'))

        order.amount_paid = Decimal('100')
        order.save()
        self.assertEqual(order.payment_status, 'PAID')

    def test_completed_at_follows_status(self):
        order = self._order()
        self.assertIsNone(order.completed_at)

        order.status = 'DONE'
        order.save()
        self.assertIsNotNone(order.completed_at)

        order.status = 'REVISION'
        order.save()
        self.assertIsNone(order.completed_at)

    def test_whatsapp_digits_adds_country_code(self):
        self.assertEqual(self._order(whatsapp='7833 6238').whatsapp_digits, '26878336238')
        self.assertEqual(self._order(whatsapp='+268 7833 6238').whatsapp_digits, '26878336238')


class OrderFlowTests(TestCase):

    def setUp(self):
        self.service = make_service()

    def test_valid_order_is_saved_and_priced(self):
        response = self.client.post(reverse('place_order'), order_payload(self.service))

        order = Order.objects.get()
        self.assertRedirects(
            response,
            reverse('order_tracking', args=[order.tracking_number])
        )
        self.assertEqual(order.quoted_price, Decimal('740.00'))
        self.assertEqual(order.status, 'NEW')

    def test_order_sends_owner_and_customer_emails(self):
        self.client.post(reverse('place_order'), order_payload(self.service))
        self.assertEqual(len(mail.outbox), 2)

    def test_invalid_input_keeps_what_was_typed(self):
        response = self.client.post(
            reverse('place_order'),
            order_payload(self.service, whatsapp='abc', customer_name='Keep Me')
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Keep Me')
        self.assertEqual(Order.objects.count(), 0)

    def test_bad_service_id_does_not_crash(self):
        response = self.client.post(
            reverse('place_order'),
            order_payload(self.service, service='abc')
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 0)

    def test_past_deadline_rejected(self):
        yesterday = (timezone.localdate() - timedelta(days=1)).isoformat()
        response = self.client.post(
            reverse('place_order'),
            order_payload(self.service, deadline=yesterday)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 0)

    def test_inactive_service_cannot_be_ordered(self):
        self.service.is_active = False
        self.service.save()

        self.client.post(reverse('place_order'), order_payload(self.service))
        self.assertEqual(Order.objects.count(), 0)

    def test_honeypot_blocks_bots(self):
        self.client.post(
            reverse('place_order'),
            order_payload(self.service, website='http://spam.example')
        )
        self.assertEqual(Order.objects.count(), 0)


class TrackingTests(TestCase):

    def setUp(self):
        self.service = make_service()
        self.client.post(reverse('place_order'), order_payload(self.service))
        self.order = Order.objects.get()

    def test_lookup_finds_order_case_insensitively(self):
        response = self.client.post(
            reverse('track_order'),
            {'tracking_number': self.order.tracking_number.lower()}
        )
        self.assertContains(response, 'Order found')

    def test_lookup_accepts_code_without_prefix(self):
        response = self.client.post(
            reverse('track_order'),
            {'tracking_number': self.order.tracking_number[3:]}
        )
        self.assertContains(response, 'Order found')

    def test_unknown_number_shows_error(self):
        response = self.client.post(
            reverse('track_order'),
            {'tracking_number': 'NQ-00000000'}
        )
        self.assertContains(response, 'No order was found')

    def test_repeated_wrong_guesses_are_blocked(self):
        for _ in range(8):
            self.client.post(reverse('track_order'), {'tracking_number': 'NQ-00000000'})

        response = self.client.post(
            reverse('track_order'),
            {'tracking_number': self.order.tracking_number}
        )
        self.assertContains(response, 'Too many unsuccessful attempts')

    def test_details_page_and_404(self):
        ok = self.client.get(reverse('order_tracking', args=[self.order.tracking_number]))
        self.assertEqual(ok.status_code, 200)

        missing = self.client.get(reverse('order_tracking', args=['NQ-FFFFFFFF']))
        self.assertEqual(missing.status_code, 404)


class ContactTests(TestCase):

    def payload(self, **overrides):
        data = {
            'name': 'Sipho',
            'email': 'sipho@example.com',
            'phone': '+268 7971 7729',
            'service': 'Logo Design',
            'budget': 'Below E500',
            'message': 'I need a logo for my new shop.',
            'website': '',
        }
        data.update(overrides)
        return data

    def test_enquiry_is_saved_and_owner_emailed(self):
        response = self.client.post(reverse('contact'), self.payload())

        self.assertRedirects(response, reverse('contact'))
        self.assertEqual(Enquiry.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_honeypot_blocks_bots(self):
        self.client.post(reverse('contact'), self.payload(website='spam'))
        self.assertEqual(Enquiry.objects.count(), 0)

    def test_short_message_rejected(self):
        self.client.post(reverse('contact'), self.payload(message='hi'))
        self.assertEqual(Enquiry.objects.count(), 0)


class PublicPageTests(TestCase):

    def test_pages_load(self):
        make_service()

        for name in ['home', 'services', 'about', 'portfolio', 'contact',
                     'place_order', 'track_order']:
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_inactive_services_hidden(self):
        make_service(name='Hidden Service', is_active=False)
        response = self.client.get(reverse('services'))
        self.assertNotContains(response, 'Hidden Service')


class AdminActionTests(TestCase):

    def test_bulk_status_updates_completed_at(self):
        from django.contrib.auth import get_user_model

        admin_user = get_user_model().objects.create_superuser('boss', 'b@example.com', 'pass12345!')
        self.client.force_login(admin_user)

        service = make_service()
        self.client.post(reverse('place_order'), order_payload(service))
        order = Order.objects.get()

        self.client.post(
            reverse('admin:shop_order_changelist'),
            {'action': 'mark_done', '_selected_action': [order.pk]}
        )

        order.refresh_from_db()
        self.assertEqual(order.status, 'DONE')
        self.assertIsNotNone(order.completed_at)
