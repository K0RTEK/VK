import pandas as pd

df = pd.read_csv('train_data.csv')
df=df['text']
df.to_csv('train_data2.csv',index=False)