import datetime

import pandas as pd
import numpy as np

import statsmodels.api as sm
import matplotlib.pyplot as plt
import plotly.express as px

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import ElasticNet, Lasso

outlier_df = pd.read_csv('./output/outlier_df.csv')

fig = px.scatter(
    outlier_df,
    x='Rated power in kVA',
    y='Transformer unit price in EUR',
    color='Outlier',
    hover_data='Project name'
)
# Update the layout to position the legend inside the bottom-right
fig.update_layout(
    legend=dict(
        x=1,              # Position x: Right of the plot (1 is the far right)
        y=0,              # Position y: Bottom of the plot (0 is the bottom)
        xanchor='right',   # Anchor legend's x-position to the right
        yanchor='bottom',  # Anchor legend's y-position to the bottom
        bgcolor='rgba(255, 255, 255, 0.5)'  # Optional: Set a semi-transparent background for the legend
    )
)
fig.show()