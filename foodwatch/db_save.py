from sqlalchemy import Date, cast, inspect
from sqlalchemy import create_engine
import pandas as pd
import sqlite3

'#1.Step: Create a db'
sqlite3

def convert_sqlalchemy_todict(obj):
    """
    Converts a sqlalchemy oject to a dict
    :param obj:
    :return:
    """
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}

mysql_path = 'postgres://diyqhmcpqznxqh:6bfd76c3b1810ef06e06867d8806f0814b45bea09a3f1aa70f0e1fb81b3c2c4c@ec2-52-207-93-32.compute-1.amazonaws.com:5432/dc2cbh2ac1dp2p'

engine = create_engine(mysql_path, echo=True)

q = engine.connect()
with engine.connect() as connection:
    result = connection.execute("SELECT * FROM food")

query_result = [convert_sqlalchemy_todict(x) for x in result]
'#2.Step: Get the current sum of the day'
df = pd.DataFrame(query_result)


