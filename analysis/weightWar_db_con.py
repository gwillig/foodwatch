import sqlite3
import pandas as pd

"""
File to convert the .db from the app weightwar to csv
"""
db = sqlite3.connect('weight_041020_073705_auto.db')
table = pd.read_sql_query("SELECT * from weightdatum", db)
table.to_csv("weight.csv")

