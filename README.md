# django_libcheck
Cybersecurity check of libraries you import in your Django projects
## Install `django_libcheck` package in the Django project virtual env
Clone this github repository:
  ```
git clone https://github.com/sesnolabs/django_libcheck.git
  ```
Navigate the virtual env where the `django_libcheck` package will be installed.
Install it:
  ```
pip install -e /path/to/django_libcheck/location
  ```
or with pipenv
  ```
pipenv install -e /path/to/django_libcheck/location
  ```
## Update all Django projects where libraries have to be checked
Navigate Django project `settings.py` file, eg:
  ```
cd django_project
nano django_project/settings.py
  ```
Update `INSTALLED_APPS` and add the app `libcheck`:
  ```
INSTALLED_APPS = [
    ...
    'libcheck',
    ...
]
  ```
At the end of the `settings.py` file, add the following:
  ```
PIPFILE_FULL_PATH = '/full/path/Pipfile'  # Set PIPFILE_FULL_PATH = None if there is no Pipfile for the project
LBC_SAFETY_NOTICES_EMAIL = 'your_email@domain.extension'
LBC_API_KEY = 'your-api-key'
LBC_OPTIONAL_AUTH_URL = None
LBC_OPTIONAL_AUTH_HEADERS = None
LBC_TEST = False  # If True, a notification is sent to LBC_SAFETY_NOTICES_EMAIL even if no safety alert
LBC_LIBRARIES = [
    # If PIPFILE_FULL_PATH is None, update this libraries list, no need to update otherwise
    'django', 'os', 'sys',  # default Django libraries
    'setuptools', 'warnings', 'requests',  # libcheck required libraries
]
LBC_VERIFY_SSL = True
LBC_NORELOAD = True  # run application once without the '--noreload' option
  ```
and add the Pipfile path for `PIPFILE_FULL_PATH` variable, or add libraries that have to be checked in the `LIBRARIES` variable if no Pipfile for the project.
Update the email `SAFETY_NOTICES_EMAIL` to be notified once a cybersecurity alert related to a library arise.
It is now almost done!
At this point, it is already possible to manually check the libraries of the Django project libraries:
  ```
./manage.py check_libraries
  ```
## Activate auto-check (safer) with the command `./manage.py runserver`
Navigate the `manage.py` file of the Django projects, eg:
  ```
cd django_project
nano manage.py
  ```
Replace `import sys` with:
  ```
import sys
from libcheck.management.commands import check_libraries
  ```
and at the end of the `main()` method, replace `execute_from_command_line(sys.argv)` with:
  ```
    check_libraries.Command().handle()
    execute_from_command_line(sys.argv)
  ```
It is done!
The command `./manage.py runserver` will now also activate an auto-check of all libraries.
