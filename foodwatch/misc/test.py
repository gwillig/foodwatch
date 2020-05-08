import pandas as pd
import os

os.chdir('./foodwatch/misc')

df_merge = pd.read_csv("df_merge.csv")

'#1.Step: Convert the timestamp_obj into panday datetime'

df_merge["timestamp_obj"]= pd.to_datetime((df_merge["timestamp_obj"])).dt.floor('d')

df_grouped = df_merge.groupby(by=df_merge['timestamp_obj'].dt.date).sum()

"2.1.Step: Inject bulk_items into db"
bulk_items1={"0":"""
                         Proteinpulver_25_g,90
                         Leinsamen_20g,106
                         Apfelkuchen_Hälfte,50
                         Hafer_50_g,180
                        """,
            "1":"""
                         Proteinpulver_25_g,90
                         Leinsamen_20g,106
                         Apfelkuchen_Hälfte,50
                         Hafer_50_g,180
                        """}
HM.bulk_items=json.dumps(bulk_items1)
db.session.commit()