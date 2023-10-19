from setuptools import setup, find_packages

setup(
    name="django_libcheck",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        "Django",
        "requests",
    ],
)
