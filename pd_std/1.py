import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

dates = pd.date_range('20130101', periods=6)
df = pd.DataFrame(np.random.randn(6, 4), index=dates, columns=list('ABCD'))
df1 = df.reindex(index=dates[0:4], columns=list(df.columns) + ['E'])
df1.loc[dates[0]:dates[1], 'E'] = 1
a = df1.dropna(how='any')
# print(df)
# print(df.apply(lambda x: x.max() - x.min()))
s = pd.Series(np.random.randint(0, 7, size=10))
print(s)
print(s.value_counts())
