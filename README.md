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
Add the end of the `settings.py` file, add the following:
  ```
TEST = False
LIBRARIES = 'warnings, requests, add-your-project-libraries-here'
SAFETY_NOTICES_EMAIL = 'your_email@domain.extension'
API_KEY = 'your-api-key'
OPTIONAL_AUTH_URL = None
OPTIONAL_AUTH_HEADERS = None
  ```
It is now almost done!
At this point, it is already possible to manually check the libraries of the Django project libraries:
  ```
./manage.py check_libraries
  ```
## Activate auto-check (safer) with the command `./manage.py runserver`
Navigate the `manage.py` file of the Django projects
