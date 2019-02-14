import csv
import pandas as pd
import os

from column_mapping import DESIRED, MAPPING


directory = os.fsencode('/output')
#column_names = set()
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    df = pd.read_csv(f'output/{filename}')
    df.rename(MAPPING,axis='columns',inplace=True)
    #print(list(df))
    for field in DESIRED:
       if field not in df:
          df[field] = ''
    df = df[DESIRED]
    #df = df.filter(DESIRED,axis='columns')
    #print(df)
    df.to_csv(f'output/{filename}', index=False)
"""    column_names |= set(list(df))
 with open('head.txt','w') as f:
    f.write('\n'.join(column_names)) """

