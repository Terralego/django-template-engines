#!/usr/bin/env python3
from os import environ
from sys import exit as sys_exit

from django import setup
from django.conf import settings
from django.test.utils import get_runner

if __name__ == '__main__':
    environ['DJANGO_SETTINGS_MODULE'] = 'test_template_engines.settings'
    setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['test_template_engines.tests'])
    sys_exit(bool(failures))
