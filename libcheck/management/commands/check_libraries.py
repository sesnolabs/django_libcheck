#!/usr/bin/env python3
"""libcheck commands"""
import os
import warnings
import requests
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from libcheck import libcheck_config

class CheckerCommand:

    test = None
    noreload = None
    pipfile_full_path = None
    url = None
    libraries = None
    safety_notice_email = None
    api_key = None
    optional_auth_url = None
    optional_auth_headers = None
    verify = None

    def __init__(self):
        self.test = False
        self.noreload = False
        self.pipfile_full_path = None
        self.url = libcheck_config.DEFAULT_URL
        self.libraries = libcheck_config.DEFAULT_LIBRARIES
        self.safety_notice_email = ''
        self.api_key = ''
        self.optional_auth_url = None
        self.optional_auth_headers = None
        self.verify = True

    def check(self, _data):
        reloaded = False
        msg = None
        try:
            if self.noreload:
                try:
                    if not os.environ.get("LIBRARIES_CHECKED"):
                        os.environ["LIBRARIES_CHECKED"] = "True"
                    else:
                        reloaded = True
                except Exception as exc:
                    warnings.warn(f"Environment variable state issue. Option '--noreload' disable. Error: {exc}")
            if reloaded:
                return False, msg
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
            response = requests.post(
                self.url, headers=headers, data=_data, verify=self.verify,
                timeout=(libcheck_config.CONNECT_TIMEOUT, libcheck_config.READ_TIMEOUT)
            )
            if response.status_code != 200:
                warnings.warn(f"LibrariesCheck Error: POST request failed. response.text: {response.text}")
            else:
                try:
                    response_text = json.loads(response.text)
                    msg = response_text['result']['message']
                except Exception as exc:
                    msg = f"LibrariesCheck log: Project libraries have been checked. "
                    msg += f"Warning! Failed to read response.text: {exc}."
        except Exception as exc:
            warnings.warn(f"LibrariesCheck Error: {exc}")
            return False, msg
        return True, msg

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
                # Add default libraries
                for lib in libcheck_config.DEFAULT_LIBRARIES:
                    if lib in libraries:
                        continue
                    resp += f'{lib},'
            except Exception as exc:
                warnings.warn(f"File /django_libcheck/libcheck/libcheck_config.py' has been damaged. Error: {exc}")
                resp = f''
        return resp


class Command(BaseCommand):
    help = "Method to ensure project libraries are safe with command './manage.py' check_libraries"

    def handle(self, *args, **options):
        try:
            cmd = CheckerCommand()
            cmd.test = settings.LBC_TEST
            cmd.verify = settings.LBC_VERIFY_SSL
            cmd.noreload = settings.LBC_NORELOAD
            cmd.pipfile_full_path = settings.PIPFILE_FULL_PATH
            cmd.libraries = settings.LBC_LIBRARIES
            cmd.safety_notice_email = settings.LBC_SAFETY_NOTICES_EMAIL
            if settings.LBC_OPTIONAL_AUTH_URL is not None:
                cmd.url = str(settings.LBC_OPTIONAL_AUTH_URL)
            if settings.LBC_OPTIONAL_AUTH_HEADERS is None:
                cmd.api_key = str(settings.LBC_API_KEY)
            else:
                cmd.optional_auth_headers = settings.LBC_OPTIONAL_AUTH_HEADERS
            libraries = cmd.get_libraries()
            checked, msg = cmd.check(libraries)
            if checked:
                self.stdout.write(f"\n{msg}\n\n")
        except Exception as exc:
            warnings.warn(
                f"LibrariesCheck failed. May have encountered misconfiguration in settings.py file. Error: {exc}"
            )
