"""
Email backend that sends through Brevo's HTTPS API.

Render's free web services block the normal SMTP ports (25, 465, 587), so
Django's SMTP backend times out there. An HTTPS request on port 443 is not
blocked. No extra Python package is needed.

Setup: create a free Brevo account, verify your sender address, create an API
key, then set BREVO_API_KEY and DEFAULT_FROM_EMAIL on Render. The address in
DEFAULT_FROM_EMAIL must be a sender you verified in Brevo.
"""

import json
import logging
import urllib.error
import urllib.request
from email.utils import parseaddr

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)


class BrevoEmailBackend(BaseEmailBackend):
    api_url = 'https://api.brevo.com/v3/smtp/email'

    def send_messages(self, email_messages):
        api_key = getattr(settings, 'BREVO_API_KEY', '')

        if not api_key:
            if not self.fail_silently:
                raise ValueError('BREVO_API_KEY is not set.')
            return 0

        sent = 0

        for message in email_messages:
            name, address = parseaddr(
                message.from_email or settings.DEFAULT_FROM_EMAIL
            )

            sender = {'email': address}
            if name:
                sender['name'] = name

            payload = {
                'sender': sender,
                'to': [{'email': recipient} for recipient in message.to],
                'subject': message.subject,
                'textContent': message.body,
            }

            if message.reply_to:
                payload['replyTo'] = {'email': message.reply_to[0]}

            request = urllib.request.Request(
                self.api_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    'api-key': api_key,
                    'content-type': 'application/json',
                    'accept': 'application/json',
                },
                method='POST',
            )

            try:
                with urllib.request.urlopen(request, timeout=10) as response:
                    if 200 <= response.status < 300:
                        sent += 1
            except (urllib.error.URLError, OSError) as error:
                logger.error('Brevo email failed: %s', error)
                if not self.fail_silently:
                    raise

        return sent
