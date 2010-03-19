#!/usr/bin/env python
from setuptools import setup, find_packages

LONG_DESCRIPTION = """
An application to allow for other apps to easily store site based configurations
"""

VERSION = "0.1.alpha"

setup(name='django-configstore',
      version=VERSION,
      description='An application to allow for other apps to easily store site based configurations',
      long_description=LONG_DESCRIPTION,
      author='Jason Kraus',
      author_email='zbyte64@gmail.com',
      url='http://github.com/cuker/django-configstore',
      packages=find_packages(exclude=['ez_setup', 'test', 'tests']),
      test_suite='tests.runtests.runtests',
     )
