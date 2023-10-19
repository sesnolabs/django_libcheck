#!/usr/bin/env python3
"""libcheck commands"""
import warnings
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from libcheck import libcheck_config

class CheckerCommand:

    test = None
    url = None
    libraries = None
    safety_notice_email = None
    api_key = None
    optional_auth_url = None
    optional_auth_headers = None

    def __init__(self):
        self.test = False
        self.url = libcheck_config.DEFAULT_URL
        self.libraries = libcheck_config.DEFAULT_LIBRARIES
        self.safety_notice_email = ''
        self.api_key = ''
        self.optional_auth_url = None
        self.optional_auth_headers = None

    def check(self):
        try:
            # Build headers
            headers = {
                'Content-Type': 'application/json',
                'email': str(self.safety_notice_email),
                'test': str(self.test),
            }
            if self.optional_auth_headers is None:
                headers['apiKey'] = str(self.api_key)
            else:
                headers.update(self.optional_auth_headers)
            # Build POST data
            if isinstance(self.libraries, str):
                data = self.libraries
            else:
                if not isinstance(self.libraries, list):
                    self.libraries = libcheck_config.DEFAULT_LIBRARIES
                data = f''
                for lib in self.libraries:
                    data += f'{lib},'
            # POST API request
            response = requests.post(self.url, headers=headers, data=data)
            if response.status_code != 200:
                warnings.warn(f"LibrariesCheck Error: POST request failed. response.text: {response.text}")
        except Exception as exc:
            warnings.warn(f"LibrariesCheck Error: {exc}")
        return

class Command(BaseCommand):
    help = 'Method to ensure project libraries are safe with command ./manage.py check_libraries'

    def handle(self, *args, **options):
        self.stdout.write('Method to ensure project libraries are safe with command ./manage.py check_libraries')
        cmd = CheckerCommand()
        try:
            cmd.test = settings.TEST
            cmd.LIBRARIES = settings.LIBRARIES
            cmd.SAFETY_NOTICES_EMAIL = settings.SAFETY_NOTICES_EMAIL
            if settings.OPTIONAL_AUTH_URL is not None:
                cmd.url = str(settings.OPTIONAL_AUTH_URL)
            if settings.OPTIONAL_AUTH_HEADERS is None:
                cmd.api_key = str(settings.API_KEY)
            else:
                cmd.optional_auth_headers = settings.OPTIONAL_AUTH_HEADERS
        except Exception as exc:
            warnings.warn(f"LibrariesCheck Error: {exc}")
        cmd.check()
