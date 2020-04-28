import unittest
from .models import setup_db, Misc, Food, Home_misc
from .app import create_app
from .models import insert_data
import json
import os
import pandas as pd

"""
Test user with no permissions:
user:  unauthorizeduser017@gmail.com
pw: Test123!

"""
class Foodwatchgw_backend(unittest.TestCase):
    """This class represents the trivia test case"""

    @classmethod
    def setUpClass(cls):
        """Define test variables and initialize app."""
        if "jwt_bearer" in os.environ.keys():
            cls.jwt_bearer = os.environ["jwt_bearer"]
        else:
            with open('foodwatch/env.json', 'r') as env_file:
                env_dict = json.load(env_file)
                cls.jwt_bearer = env_dict["jwt_bearer"]
        if "jwt_bearer_unauthorized" in os.environ.keys():
            cls.jwt_bearer_unauthorized = os.environ["jwt_bearer_unauthorized"]
        else:
            with open('foodwatch/env.json', 'r') as env_file:
                env_dict = json.load(env_file)
                cls.jwt_bearer_unauthorized = env_dict["jwt_bearer_unauthorized"]

        cls.app = create_app(dbms="sqlite3",test_config=True)
        project_dir = os.path.dirname(os.path.abspath(__file__))
        database_path = "sqlite:///{}".format(os.path.join(project_dir, "database_test.db"))
        cls.db = setup_db(cls.app, database_path)
        cls.client = cls.app.test_client

    def tearDown(self):
        """Executed after reach test"""
        pass

    def setUp(self):
        """Executed before reach test"""
        '#.Step: Delete all records in database because the test change the data'
        for el in [Food,Misc,Home_misc]:
            self.db.session.query(el).delete()
            self.db.session.commit()
        if self.db.session.query(Food).count()==0:
            insert_data(self.db)

    @classmethod
    def tearDownClass(cls):
        os.remove("foodwatch/database_test.db")

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
        """
        Test delete misc for authorized user and unauthorized user

        """
        for k,v in {"jwt_auth":[self.jwt_bearer,200],"jwt_unauthorized":[self.jwt_bearer_unauthorized,500]}.items():
            with self.subTest(k):
                response = self.client().delete('/misc', json={"data":1},headers={'Content-Type': 'application/json',
                                                                                  "Authorization": "Bearer " +v[0]},
                                                 content_type='application/json')
                # Check response
                self.assertEqual(response.status_code, v[1])

    def test_post_misc_data(self):
        """
        Test post misc for authorized user and unauthorized user

        """
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
        for k,v in {"jwt_auth":[self.jwt_bearer,200],"jwt_unauthorized":[self.jwt_bearer_unauthorized,500]}.items():
            with self.subTest(k):
                response = self.client().post('/misc_data',headers={'Content-Type': 'application/json',
                                                                    "Authorization": "Bearer " +v[0]},
                                              content_type='application/json',  json=data)
                # Check response
                self.assertEqual(response.status_code, v[1])

    def test_post_data_today(self):
        """
        Test post data today for authorized user and unauthorized user

        """
        data = {"data":
                    {
                        "timestamp_epoch": 1587987510119,
                        "name": "Orange",
                        "calorie": "100",
                        "total_calorie_plan": "1600"
                    }
                }
        for k,v in {"jwt_auth":[self.jwt_bearer,200],"jwt_unauthorized":[self.jwt_bearer_unauthorized,500]}.items():
            with self.subTest(k):
                response = self.client().post('/data_today', json=data,headers={'Content-Type': 'application/json',
                                                                                "Authorization": "Bearer " +v[0]},
                                              content_type='application/json')
                # Check response
                self.assertEqual(response.status_code, v[1])

    def test_delete_data_today(self):

        for k,v in {"jwt_auth":[self.jwt_bearer,200],"jwt_unauthorized":[self.jwt_bearer_unauthorized,500]}.items():
            with self.subTest(k):
                response = self.client().delete('/data_today', json={"data":1},headers={'Content-Type': 'application/json',
                                                                                        "Authorization": "Bearer " +v[0]}
                                                ,content_type='application/json')
                # Check response
                self.assertEqual(response.status_code, v[1])




    def test_merge_food_misc(self):
        df_merge= self.app.merge_food_misc(self.db)
        df_test = pd.read_csv("foodwatch/df_merge_food_misc_testcase.csv")
        '#.Step: Adapt the type of the df_test'
        df_test["timestamp_obj"] = pd.to_datetime((df_test["timestamp_obj"]))
        df_test["amount_weight"] = df_test["amount_weight"].astype("float64")
        pd._testing.assert_frame_equal(df_test[['timestamp_obj','amount_weight', 'amount_steps','calorie']],
                                       df_merge[['timestamp_obj','amount_weight', 'amount_steps','calorie']])

