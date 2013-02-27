#!/usr/bin/env python
from setuptools import setup, find_packages

LONG_DESCRIPTION = """
An application to allow for other apps to easily store site based configurations
"""

VERSION = "0.1"

setup(name='django-configstore',
      version=VERSION,
      description='An application to allow for other apps to easily store site based configurations',
      long_description=LONG_DESCRIPTION,
      author='Jason Kraus',
      author_email='zbyte64@gmail.com',
      url='http://github.com/cuker/django-configstore',
      packages=find_packages(exclude=['ez_setup', 'test', 'tests']),
      test_suite='tests.runtests.runtests',
      tests_require=(
        'pep8',
        'coverage',
        'django',
        'nose',
        'django-nose',
      ),
      include_package_data=True,
      license = 'BSD',
      classifiers=[
          'Programming Language :: Python',
          'Operating System :: OS Independent',
          'Natural Language :: English',
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          "Framework :: Django",
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],
     )
