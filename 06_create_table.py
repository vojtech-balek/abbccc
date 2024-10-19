import pandas as pd
import numpy as np

import plotly.graph_objects as go

df = pd.DataFrame({
    "Quantity": [0.0115],
    "Rated power in kVA": [0.6855],
    "No load loss": [1.046e-05],
    "Full load loss at 75 degrees": [1.289e-06],
    "Full load loss at 120 degrees": [-4.004e-06],
    "Rated voltage primary side": [0.1767],
    "Aluminum price per kg": [0.10482],
    "Copper price per kg": [0.1169],
    "Oil type transformer": [0.6070],
    "Primary winding is copper": [0.061096],
    "Secondary winding is copper": [-0.027261],
    "Secondary material price": [0.023945]
})

df_T = df.T.reset_index().copy()
df_T.columns = ['Variable', 'Coefficient']
df_T = df_T.sort_values(by='Coefficient', ascending=False)
df_T['Coefficient'] = df_T['Coefficient'].apply(lambda x: round(x, 3))

fig = go.Figure(
    data=[
        go.Table(
            header=dict(values=df_T.columns),
            cells=dict(values=[df_T['Variable'], df_T['Coefficient']]))])
fig.show()