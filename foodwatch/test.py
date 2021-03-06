import unittest
import json
import os
import pandas as pd
import sys
from multiprocessing import Process
from selenium import webdriver
import threading
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
sys.path.append("foodwatch")
from .models import setup_db, Misc, Food, Home_misc
from .app import create_app
from .models import insert_data

"""
Test user with no permissions:
user:  unauthorizeduser017@gmail.com
pw: Test123!

"""
class Foodwatchgw_basic(unittest.TestCase):
    """
    Contains the setUpClass, tearDown etc

    """
    @classmethod
    def setUpClass(cls):
        """Define test variables and initialize app."""
        '#1.Step: Start flask test server'
        cls.app = create_app(dbms="sqlite3",test_config=True)
        project_dir = os.path.dirname(os.path.abspath(__file__))
        database_path = "sqlite:///{}".format(os.path.join(project_dir, "database_test.db"))
        cls.db = setup_db(cls.app, database_path)
        cls.db.session.query(Misc).delete()
        cls.db.session.query(Food).delete()
        cls.db.session.query(Home_misc).delete()
        insert_data(cls.db)

        cls.client = cls.app.test_client
        'Attention: in auth0 it must be included in the "Allowed Callback URLs" '
        cls.host_port = "7000"

        '#1.1.Step: Start test serer'
        cls.test_server = Process(target=create_app().run, args=("0.0.0.0", cls.host_port))
        cls.test_server.start()
        '#1.Step: Load env variables'
        for el in ["admin","viewer"]:
            if el[0] in os.environ.keys():
                exec(f'cls.{el} = {os.environ[el]}')
            else:
                with open('foodwatch/env.json', 'r') as env_file:
                    env_dict = json.load(env_file)
                    exec(f'cls.{el} = {env_dict[el]}')

        '#2.Step: Get jwt'
        driver_wait=30
        for el in [cls.admin,cls.viewer]:
            driver = webdriver.Chrome("foodwatch/chromedriver")
            driver.get("localhost:" + cls.host_port)
            login_btn = driver.find_element_by_id("loginlink")
            login_btn.click()
            WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.ID, "1-email")))
            email_input = driver.find_element_by_id("1-email")
            email_input.send_keys(el["email"])
            pwd_input = driver.find_element_by_xpath("//input[@placeholder='your password']")
            pwd_input.send_keys(el["pwd"])
            login_span = driver.find_element_by_class_name("auth0-label-submit")
            login_span.click()
            WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.ID, "percent")))
            el["jwt_token"] = driver.execute_script("return localStorage.getItem('jwt')")
            driver.close()

    def tearDown(self):
        """Executed after reach test"""
        pass
    @classmethod
    def teardownClass(cls):
        os.remove("foodwatch/database_test.db")
    def setUp(self):
        """Executed before reach test"""
        '#.Step: Delete all records in database because the test change the data'
        for el in [Food,Misc,Home_misc]:
            self.db.session.query(el).delete()
            self.db.session.commit()
        if self.db.session.query(Food).count()==0:
            insert_data(self.db)

class Backend(Foodwatchgw_basic):
    """The test case for the backend"""

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

    def test_get_data_today(self):

        response = self.client().get('/data_today')
        # Check response
        self.assertEqual(response.status_code, 200)

    def test_get_bulk_items(self):

        response = self.client().get('/bulk_items/1')
        # Check response
        self.assertEqual(response.status_code, 200)

    def test_post_bulk_items(self):

        """
        Test post bulk_items for authorized user and unauthorized user

        """
        for k,v in {"jwt_auth":[self.admin["jwt_token"],200],"jwt_unauthorized":[self.viewer["jwt_token"],4011]}.items():
            with self.subTest(k):
                response = self.client().post('/bulk_items', json={"bulk_items": "Test_123","bulk_slot":"test"},
                                                headers={'Content-Type': 'application/json',
                                                                                  "Authorization": v[0]},
                                                 content_type='application/json')
                # Check response
                self.assertEqual(response.status_code, v[1])


    def test_get_data_today(self):

        response = self.client().get('/data_today')
        # Check response
        self.assertEqual(response.status_code, 200)

    def test_delete_misc(self):
        """
        Test delete misc for authorized user and unauthorized user

        """
        for k,v in {"jwt_auth":[self.admin["jwt_token"],200],"jwt_unauthorized":[self.viewer["jwt_token"],4011]}.items():
            with self.subTest(k):
                response = self.client().delete('/misc', json={"data":1},headers={'Content-Type': 'application/json',
                                                                                  "Authorization": v[0]},
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
        for k,v in {"jwt_auth":[self.admin["jwt_token"],200],"jwt_unauthorized":[self.viewer["jwt_token"],4011]}.items():
            with self.subTest(k):
                response = self.client().post('/misc_data',headers={'Content-Type': 'application/json',
                                                                    "Authorization": v[0]},
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
        for k,v in {"jwt_auth":[self.admin["jwt_token"],200],"jwt_unauthorized":[self.viewer["jwt_token"],4011]}.items():
            with self.subTest(k):
                response = self.client().post('/data_today', json=data,headers={'Content-Type': 'application/json',
                                                                                "Authorization": v[0]},
                                              content_type='application/json')
                # Check response
                self.assertEqual(response.status_code, v[1])

    def test_delete_data_today(self):

        for k,v in {"jwt_auth":[self.admin["jwt_token"],200],"jwt_unauthorized":[self.viewer["jwt_token"],4011]}.items():
            with self.subTest(k):
                response = self.client().delete('/data_today', json={"data":1},headers={'Content-Type': 'application/json',
                                                                                        "Authorization": v[0]}
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


class Frontend(Foodwatchgw_basic):


    def test_home_bgn(self):
        "Tests all buttons on the home.html"
        driver_wait=30

        for el in [[self.admin,"Successfully submitted to database"]
                    ,[self.viewer,'Permission check fail. The person doenst has the required permission']]:
            for btn in ["btn_add", "btn_bulk"]:
                driver = webdriver.Chrome("foodwatch/chromedriver")
                driver.get("localhost:"+self.host_port)
                login_btn = driver.find_element_by_id("loginlink")
                login_btn.click()
                WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.ID, "1-email")))
                email_input = driver.find_element_by_id("1-email")
                email_input.send_keys(el[0]["email"])
                pwd_input = driver.find_element_by_xpath("//input[@placeholder='your password']")
                pwd_input.send_keys(el[0]["pwd"])
                login_span = driver.find_element_by_class_name("auth0-label-submit")
                login_span.click()
                WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.ID, "percent")))
                el[0]["jwt_token"] = driver.execute_script("return localStorage.getItem('jwt')")
                '#.Step: Enter food name'
                food_name = driver.find_element_by_id("input_name")
                food_name.send_keys("Orange")
                '#.Step: Enter food cal'
                WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.ID, "input_cal")))
                food_cal = driver.find_element_by_id("input_cal")
                '#.Step: '
                food_cal.clear()
                food_cal.send_keys("150")
                '#.Step: Click add btn'
                WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.ID, btn)))
                add_btn = driver.find_element_by_id(btn)
                driver.execute_script(f"document.querySelector('#{btn}').click();")
                driver.execute_script(f"document.querySelector('#{btn}').click();")
                with self.subTest(el[0]):
                    WebDriverWait(driver, driver_wait).until(
                        EC.text_to_be_present_in_element((By.ID, "msg_db"), el[1]))
                    msg_db = driver.find_element_by_id("msg_db")
                    self.assertEqual(msg_db.text, el[1])
                '#Test btn cal ratio'
                btn_cal_ratio = driver.find_element_by_id("btn_cal_ratio")
                btn_cal_ratio.click()
                with self.subTest("btn_cal_ratio"):
                    '#If btn_cal_ratio works the will be an output in cal_output'
                    input_cal_output = driver.find_element_by_id("cal_output")
                    self.assertTrue(input_cal_output.text!="" )
                '#Test btn motivation'
                btn_motiv = driver.find_element_by_id("btn_motiv")
                btn_motiv.click()
                with self.subTest("btn_motiv"):
                    WebDriverWait(driver, driver_wait).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "motivation_div")))
                    motivation_div = driver.find_element_by_id("motivation_div")
                    '# The value of display should be none, underwise it is not visible'
                    display_value = motivation_div.value_of_css_property("display")
                    self.assertEqual(display_value,"block" )
                    motivation_div.click()
                with self.subTest("close_bulk_div"):
                    '#.Step: Click the bulk btn'
                    driver.execute_script(f"document.querySelector('#btn_bulk').click();")
                    '#.Step: Wait until the close_bulk p is clickable'
                    WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.ID, "close_bulk_div")))
                    cloclose_bulk_p = driver.find_element_by_id("close_bulk_div")
                    driver.execute_script(f"document.querySelector('#close_bulk_div').click();")
                    '# The value of display should be none, underwise it is not visible'
                    bulk_div = driver.find_element_by_id("bulk_div")
                    display_value = bulk_div.value_of_css_property("display")
                    self.assertEqual(display_value,"none" )
                with self.subTest("save_bulk_items"):
                    '#.Step: Click the bulk btn'
                    driver.execute_script(f"document.querySelector('#btn_bulk').click();")
                    '#.Step: Wait until the close_bulk p is clickable'
                    WebDriverWait(driver, driver_wait).until(EC.element_to_be_clickable((By.ID, "btn_bulk")))
                    driver.execute_script(f"document.querySelector('#btn_bulk').click();")
                    '# The text of p-tag bulk_msg should be "Items successfuly posted to database"'
                    bulk_msg_text = driver.find_element_by_id("msg_db").text
                    self.assertEqual(bulk_msg_text,el[1])

            driver.close()

            self.test_server.terminate()
if __name__ == '__main__':
    unittest.main()



    def print_out():
        import time
        for i in range(10):
            time.sleep(1)
            print("hello world")



    t = Process(target=print_out)
    t.start()
    t.terminate()