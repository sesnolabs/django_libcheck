#!/usr/bin/env python3
"""libcheck commands"""
import warnings
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from libcheck import libcheck_config

class CheckerCommand:

    test = None
    pipfile_full_path = None
    url = None
    libraries = None
    safety_notice_email = None
    api_key = None
    optional_auth_url = None
    optional_auth_headers = None

    def __init__(self):
        self.test = False
        self.pipfile_full_path = None
        self.url = libcheck_config.DEFAULT_URL
        self.libraries = libcheck_config.DEFAULT_LIBRARIES
        self.safety_notice_email = ''
        self.api_key = ''
        self.optional_auth_url = None
        self.optional_auth_headers = None

    def check(self, _data):
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
            # POST API request
            response = requests.post(self.url, headers=headers, data=_data)
            if response.status_code != 200:
                warnings.warn(f"LibrariesCheck Error: POST request failed. response.text: {response.text}")
        except Exception as exc:
            warnings.warn(f"LibrariesCheck Error: {exc}")
        return

    def get_libraries_from_pipfile(self):
        if self.pipfile_full_path is None:
            return
        libraries = []
        try:
            with open(self.pipfile_full_path, 'r') as pipfile:
                lines = pipfile.readlines()
                is_in_dependencies_section = False

                for line in lines:
                    line = line.strip()
                    if line.startswith("[") and line.endswith("]"):
                        section_name = line[1:-1].strip()
                        if section_name == "packages":
                            is_in_dependencies_section = True
                        else:
                            is_in_dependencies_section = False
                    elif is_in_dependencies_section and "=" in line:
                        library = line.split("=")[0].strip()
                        libraries.append(library)

        except FileNotFoundError:
            warnings.warn(f"Pipfile NOT found at:'{self.pipfile_full_path}'.")
            return
        except Exception as exc:
            warnings.warn(f"Failed to extract libraries from Pipfile at:'{self.pipfile_full_path}'.\n{exc}")
            return
        return libraries

    def get_libraries(self):
        libraries = self.get_libraries_from_pipfile()
        if libraries is None:
            libraries = self.libraries
        if isinstance(libraries, str):
            resp = libraries
        else:
            try:
                if not isinstance(libraries, list):
                    libraries = libcheck_config.DEFAULT_LIBRARIES
                resp = f''
                for lib in libraries:
                    resp += f'{lib},'
            except Exception as exc:
                warnings.warn(f"File /django_libcheck/libcheck/libcheck_config.py' has been damaged. Error: {exc}")
                resp = f''
        return resp


class Command(BaseCommand):
    help = 'Method to ensure project libraries are safe with command ./manage.py check_libraries'

    def handle(self, *args, **options):
        cmd = CheckerCommand()
        try:
            cmd.test = settings.TEST
            cmd.pipfile_full_path = settings.PIPFILE_FULL_PATH
            cmd.LIBRARIES = settings.LIBRARIES
            cmd.SAFETY_NOTICES_EMAIL = settings.SAFETY_NOTICES_EMAIL
            if settings.OPTIONAL_AUTH_URL is not None:
                cmd.url = str(settings.OPTIONAL_AUTH_URL)
            if settings.OPTIONAL_AUTH_HEADERS is None:
                cmd.api_key = str(settings.API_KEY)
            else:
                cmd.optional_auth_headers = settings.OPTIONAL_AUTH_HEADERS
            libraries = cmd.get_libraries()
            cmd.check(libraries)
            self.stdout.write(f"LibrariesCheck log: project libraries '{libraries}' have been checked.")
        except Exception as exc:
            warnings.warn(f"LibrariesCheck Error: {exc}")
