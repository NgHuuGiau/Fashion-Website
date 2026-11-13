#!/usr/bin/env python
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

os.environ["DJANGO_SETTINGS_MODULE"] = "core.test_settings_sqlite"

import django

django.setup()

from django.conf import settings
from django.test.utils import get_runner

runner = get_runner(settings)()
failures = runner.run_tests(["orders.test_cart"])
sys.exit(failures)
