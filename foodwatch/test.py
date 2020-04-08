import unittest
from .models import setup_db, Misc, Food
from .app import create_app
class CastingTestCase(unittest.TestCase):
    """
    :return
    """

    @classmethod
    def setUPClass(cls):
        cls.app = create_app()