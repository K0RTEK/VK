import pandas as pd

df = pd.read_csv('train_data.csv')
df=df.dropna(subset=['text'])

for i in df['text']:
    print(i)

