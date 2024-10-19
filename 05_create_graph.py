import pandas as pd
import numpy as np

import plotly.express as px

df = pd.DataFrame({
    'Quantity': [0.0115],
    'Rated power in kVA': [0.6855],
    'Rated voltage on primary side': [0.1767],
    'Aluminum price per kg': [0.10482],
    'Copper price per kg': [0.1169],
    'Oil type transformer': [0.6070],
})

df_T = df.T.reset_index().copy()
df_T.columns = ['Variable', 'Coefficient']
df_T = df_T.sort_values(by='Coefficient', ascending=False)

fig =px.bar(
    df_T, 
    x='Variable', 
    y='Coefficient', 
    title='Main price drivers'
)
fig.show()