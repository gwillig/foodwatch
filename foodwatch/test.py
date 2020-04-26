import unittest
from .models import setup_db, Misc, Food
from .app import create_app



class Foodwatchgw(unittest.TestCase):
    """This class represents the trivia test case"""

    @classmethod
    def setUpClass(cls):
        """Define test variables and initialize app."""

        cls.app = create_app(dbms="sqlite3",test_config=True)
        cls.client = cls.app.test_client

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_misc(self):
        response = self.client().get('/misc')
        # Check response
        self.assertEqual(response.status_code, 200)

    def test_home(self):
        response = self.client().get('/')
        # Check response
        self.assertEqual(response.status_code, 200)

    def test_analysis(self):
        response = self.client().get('/analysis')
        # Check response
        self.assertEqual(response.status_code, 200)

    #Need to be redone!
    def test_get_data_today(self):
        response = self.client().get('/data_today')
        # Check response
        self.assertEqual(response.status_code, 200)

    def test_delete_misc(self):
        response = self.client().delete('/misc')
        # Check response
        self.assertEqual(response.status_code, 200)

    def test_post_misc_data(self):
        response = self.client().post('/misc_data')
        # Check response
        self.assertEqual(response.status_code, 200)

    def test_post_data_today(self):
        response = self.client().post('/data_today')
        # Check response
        self.assertEqual(response.status_code, 200)

    def test_delete_data_today(self):
        response = self.client().delete('/data_today')
        # Check response
        self.assertEqual(response.status_code, 200)

    def test_merge_food_misc(self):
        self.app.merge_food_misc()

    def test_convert_sqlalchemy_todict(self):
        self.app.test_convert_sqlalchemy_todict()