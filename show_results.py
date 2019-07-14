# -*- coding: utf-8 -*-
"""show_results.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1RE-ZAxCZcn_itSxABtFWMFf9r9zXhGVg
"""

import pandas as pd

canidae_path = 'single_att_results/canidae.csv'
kitchen_path = 'single_att_results/kitchen.csv'

df_canidae = pd.read_csv(canidae_path, index_col = 0)
df_kitchen = pd.read_csv(kitchen_path, index_col = 0)

with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(df_canidae)
    print(df_kitchen)