import sqlalchemy
import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.orm import sessionmaker
import os
import json
import pandas as pd
from datetime import timezone
from datetime import datetime



'#1.Step: Connect to database'
'#1.1.Step: Get path from env.json'
database = "sqllite"
if database=="heroku":
    with open('foodwatch/env.json','r') as env_file:
        env_dict = json.load(env_file)
        database_path = env_dict["database_path"]
else:
    database_path = "sqlite:///foodwatch/database.db"
db_con = sqlalchemy.create_engine(database_path)


'#1.2.Step: Define session'
Session = sessionmaker(bind=db_con)
session = Session()
'#1.3.Step: Show that connection work'
result = db_con.execute("Select * from misc")
for row in result:
    print(row)

'#1.4.Step: convert data into csv'
table = pd.read_sql_query("Select * from home_misc", db_con)
table.to_csv("home_misc_14_06_20.csv")
'#2.Step: Add new data to database'
# db_con.execute("Insert value into table Misc(timestamp_unix,) VALUES()")

'#3.Step: Define Model to add data to db'
Base = declarative_base()
class Misc(Base):
    __tablename__ ='misc'
    id = db.Column(db.Integer, primary_key=True)
    timestamp_unix = db.Column(db.Float)
    timestamp_obj = db.Column(db.DateTime)
    amount_weight = db.Column(db.Float)
    amount_steps = db.Column(db.Integer)

class Food(Base):
    __tablename__ = 'food'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    timestamp_unix = db.Column(db.Float)
    timestamp_obj = db.Column(db.DateTime)
    calorie = db.Column(db.Integer)


    def __repr__(self):
        '1.Step: Get all actors which were involved in move'
        return f"{self.name};{self.timestamp_obj}"


'''
Example how to add data to db
m1 = Misc(amount_steps=1000, timestamp_obj=datetime.utcfromtimestamp(1590451200),
          timestamp_unix=1590451200,amount_weight=89,
          )          
session.add(m1)
session.commit()
'''
##### Add data from data_19_04.csv to db

df = pd.read_csv('misc_14_06_20.csv')
df_bulk = pd.DataFrame()
'#1.Step: Pre-processing of df'
df = df.astype({'timestamp_unix': 'int64'})
'#1.1.Step: Convert date string into date obj'
df_bulk["timestamp_obj"] = df["timestamp_unix"].apply(lambda x:datetime.utcfromtimestamp((x)))
'#1.2.Step: convert to unix'
df_bulk["timestamp_unix"] = df_bulk.timestamp_obj.apply(lambda x: x.timestamp())
df_bulk["amount_weight"] = df["amount_weight"]
df_bulk["amount_steps"] = df["amount_steps"]

'#2.Step: Add data from df_bulk to db'
bulk_list = df_bulk.to_dict("row")
bulk_list_obj = [Misc(**x) for x in bulk_list]
session.bulk_save_objects(bulk_list_obj)
session.commit()
'########Insert food data'
df = pd.read_csv('food_14_06_20.csv')
df_bulk = pd.DataFrame()
'#1.Step: Pre-processing of df'
df = df.astype({'timestamp_unix': 'int64'})
'#1.1.Step: Convert date string into date obj'
df_bulk["timestamp_obj"] = df["timestamp_unix"].apply(lambda x:datetime.utcfromtimestamp((x)))
'#1.2.Step: convert to unix'
df_bulk["timestamp_unix"] = df_bulk.timestamp_obj.apply(lambda x: x.timestamp())
df_bulk["calorie"] = df["calorie"]
df_bulk["name"] = df["name"]

'#2.Step: Add data from df_bulk to db'
bulk_list = df_bulk.to_dict("row")
bulk_list_obj = [Food(**x) for x in bulk_list]
session.bulk_save_objects(bulk_list_obj)
session.commit()


def convert_str_date_obj_utc(date_str):
    """
    Function converts a given string to a date obj with timezone utc
    :param
        date_str(str) e.g. '18/04/2020'
    :return:
        date_obj_timezone(datetime.datetime)
    """
    '#1.Step: Convert string into datetime.datetime object'
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    '#2.Step: Set timezone otherwise the conversion into unix can have some problems'
    date_obj_timezone = date_obj.replace(tzinfo=timezone.utc)
    return date_obj_timezone


'########Insert historical food data'
df = pd.read_csv('misc_2018_2020_06.csv')
df_bulk = pd.DataFrame()

'#1.1.Step: Convert date string into date obj'
df_bulk["timestamp_obj"] = df["timestamp_obj"].apply(lambda x:convert_str_date_obj_utc(x))
df_bulk["amount_weight"] = df["amount_weight"]
df_bulk["amount_steps"] = df["amount_steps"]
'#1.2.Step: convert to unix'
df_bulk["timestamp_unix"] = df_bulk.timestamp_obj.apply(lambda x: x.timestamp())


'#2.Step: Add data from df_bulk to db'
bulk_list = df_bulk.to_dict("row")
bulk_list_obj = [Misc(**x) for x in bulk_list]
session.bulk_save_objects(bulk_list_obj)
session.commit()
