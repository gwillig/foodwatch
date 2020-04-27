import unittest
from .models import setup_db, Misc, Food
from .app import create_app
from .models import insert_data
import json
import os

class Foodwatchgw(unittest.TestCase):
    """This class represents the trivia test case"""

    @classmethod
    def setUpClass(cls):
        """Define test variables and initialize app."""

        cls.app = create_app(dbms="sqlite3",test_config=True)
        project_dir = os.path.dirname(os.path.abspath(__file__))
        database_path = "sqlite:///{}".format(os.path.join(project_dir, "database_test.db"))
        cls.db = setup_db(cls.app, database_path)
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

        data = {"data": [
                          {
                            "database_id": "database_id",
                            "date": "27/4/2020",
                            "weight": "89",
                            "steps": "16000"
                          },
                          {
                            "database_id": "3",
                            "date": "28/01/2020",
                            "weight": "91.0",
                            "steps": "1200"
                          },
                        ]
           }
        response = self.client().post('/misc_data',headers={'Content-Type': 'application/json'},content_type='application/json',  json=data)
        # Check response
        self.assertEqual(response.status_code, 200)

    def test_post_data_today(self):
        data = {"data":
                    {
                        "timestamp_epoch": 1587987510119,
                        "name": "Orange",
                        "calorie": "100",
                        "total_calorie_plan": "1600"
                    }
                }
        response = self.client().post('/data_today', json=data,headers={'Content-Type': 'application/json'},content_type='application/json')
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