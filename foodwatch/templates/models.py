from sqlalchemy import Table, Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import relationship, backref
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def insert_data(db):
    a1 = Actor(first_name="John", family_name="Doe")
    a2 = Actor(first_name="Alice", family_name="Doe")
    a3 = Actor(first_name="David", family_name="Schmid")
    m1 = Movie(title="The live a John Doe")
    m1.actors.append(a1)
    m1.actors.append(a2)
    db.session.add(m1)
    db.session.add(a3)
    db.session.commit()


def setup_db(app, database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()
    return db


class Food(db.Model):
    __tablename__ = 'food'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    timestamp = db.Column(db.Float)


    def __repr__(self):
        '1.Step: Get all actors which were involved in move'
        inv_actors = [f"{x.first_name}, { x.family_name}" for x in self.actors]
        return f"{self.title}; feature: {', '.join(inv_actors)}"

