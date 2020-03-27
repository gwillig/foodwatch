from sqlalchemy import Table, Column, Integer, ForeignKey, Float,DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import relationship, backref
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime



db = SQLAlchemy()


def insert_data(db):
    a1 = Food(name="Orange", timestamp_obj=datetime.utcfromtimestamp(1585243532711/1000),
              timestamp_unix=1585243532711,
              calorie=200)
    print("data injected!")
    db.session.add(a1)
    db.session.commit()

def setup_db(app, database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()
    if len(db.session.query(Food).all())<1:
        insert_data(db)

    return db


class Food(db.Model):
    __tablename__ = 'food'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    timestamp_unix = db.Column(db.Float)
    timestamp_obj = db.Column(db.DateTime)
    calorie = db.Column(Integer)


    def __repr__(self):
        '1.Step: Get all actors which were involved in move'
        return f"{self.name};{self.timestamp_obj}"

