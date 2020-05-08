import pandas as pd
import os

os.chdir('./foodwatch/misc')

df_merge = pd.read_csv("df_merge.csv")

'#1.Step: Convert the timestamp_obj into panday datetime'

df_merge["timestamp_obj"]= pd.to_datetime((df_merge["timestamp_obj"])).dt.floor('d')

df_grouped = df_merge.groupby(by=df_merge['timestamp_obj'].dt.date).sum()


import json
bulk_items = {"0":"""Proteinpulver_25_g,90
         Leinsamen_20g,106
         Apfelkuchen_Hälfte,50
         Hafer_50_g,180""",
 "1":"""Steak_25_g,80"""}
bulk_items_s = json.dumps(bulk_items)

bulk_dict = json.loads(bulk_items_s)
