import os

# Avoid clikit calling fileno() on captured stdout on Windows under pytest
os.environ.setdefault("ANSICON", "1")

from .TestCase import TestCase
