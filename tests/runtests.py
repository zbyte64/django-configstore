import os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
test_dir = os.path.dirname(__file__)
sys.path.insert(0, test_dir)

from django.test.simple import run_tests as django_test_runner
from django.conf import settings

def runtests():
    failures = django_test_runner(['configstore'], verbosity=1, interactive=True)
    sys.exit(failures)

if __name__ == '__main__':
    runtests()

