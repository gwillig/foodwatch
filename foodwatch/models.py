from sqlalchemy import Table, Column, Integer, ForeignKey, Float,DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import relationship, backref
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime



db = SQLAlchemy()

def insert_data(db):
    a1 = Food(name="Orange_beson", timestamp_obj=datetime.utcfromtimestamp(1580000003),
              timestamp_unix=1580000003,
              calorie=200,user_email="gustavwillig@gmail.com")

    a2 = Food(name="Orange", timestamp_obj=datetime.utcfromtimestamp(1580100003),
              timestamp_unix=1580100003,
              calorie=300,user_email="gustavwillig@gmail.com")
    a3 = Food(name="Orange", timestamp_obj=datetime.utcfromtimestamp(1580200003),
              timestamp_unix=1580200003,
              calorie=400,user_email="gustavwillig@gmail.com")
    a4 = Food(name="Orange", timestamp_obj=datetime.utcfromtimestamp(1580300003),
              timestamp_unix=1580300003,
              calorie=500,user_email="gustavwillig@gmail.com")
    a5 = Food(name="Banana", timestamp_obj=datetime.utcfromtimestamp(1580300003),
              timestamp_unix=1580300003,
              calorie=500,user_email="gustavwillig@gmail.com")

    m1 = Misc(amount_steps=1000, timestamp_obj=datetime.utcfromtimestamp(1580000003),
              timestamp_unix=1580000003,amount_weight=89,
              user_email="gustavwillig@gmail.com"
              )
    m2 = Misc(amount_steps=1100, timestamp_obj=datetime.utcfromtimestamp(1580100003),
              timestamp_unix=1580100003,amount_weight=90,
              user_email="gustavwillig@gmail.com"
              )
    m3 = Misc(amount_steps=1200, timestamp_obj=datetime.utcfromtimestamp(1580200003),
              timestamp_unix=1580200003,amount_weight=91,
              user_email="gustavwillig@gmail.com"
              )

    m4 = Misc(amount_steps=1300, timestamp_obj=datetime.utcfromtimestamp(1580300003),
              timestamp_unix=1580300003, amount_weight=92,
              user_email="gustavwillig@gmail.com"
              )
    print("data injected!")
    hm1 = Home_misc(total_calories=1600)
    db.session.bulk_save_objects([hm1,a1,a2,a3,a4,a5,m1,m2,m3,m4])
    db.session.commit()

def setup_db(app,database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()
    if len(db.session.query(Food).all())<1:
        insert_data(db)
    return db

class Home_misc(db.Model):
    __table__name="home_misc"
    id = db.Column(db.Integer, primary_key=True)
    total_calories= db.Column(Integer)

class Misc(db.Model):
    __table__name ='weights'
    id = db.Column(db.Integer, primary_key=True)
    timestamp_unix = db.Column(db.Float)
    timestamp_obj = db.Column(db.DateTime)
    amount_weight = db.Column(db.Float)
    amount_steps = db.Column(Integer)
    user_email = db.Column(db.String(100))
class Food(db.Model):
    __tablename__ = 'food'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    timestamp_unix = db.Column(db.Float)
    timestamp_obj = db.Column(db.DateTime)
    calorie = db.Column(Integer)
    user_email = db.Column(db.String(100))

    def __repr__(self):
        '1.Step: Get all actors which were involved in move'
        return f"{self.name};{self.timestamp_obj}"

