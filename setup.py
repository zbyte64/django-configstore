#!/usr/bin/env python
from distutils.core import setup, find_packages

LONG_DESCRIPTION = """
An application to allow for other apps to easily store site based configurations
"""

VERSION = "0.1.alpha"

setup(name='django-configstore',
      version=VERSION,
      short_description='An application to allow for other apps to easily store site based configurations',
      description=LONG_DESCRIPTION,
      author='Jason Kraus',
      author_email='zbyte64@gmail.com',
      url='',
      packages=find_packages(exclude=['ez_setup', 'test', 'tests']),
     )
