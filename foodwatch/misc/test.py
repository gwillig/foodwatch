import pandas as pd
import os

os.chdir('./foodwatch/misc')

df_merge = pd.read_csv("df_merge.csv")

'#1.Step: Convert the timestamp_obj into panday datetime'

df_merge["timestamp_obj"]= pd.to_datetime((df_merge["timestamp_obj"])).dt.floor('d')

df_grouped = df_merge.groupby(by=df_merge['timestamp_obj'].dt.date).sum()