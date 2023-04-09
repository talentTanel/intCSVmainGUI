import altair as alt
import matplotlib.pyplot as plt
from matplotlib_inline.backend_inline import set_matplotlib_formats
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns

#set_matplotlib_formats('retina')

# Create our new styles dictionary for use in rcParams.
""" dpi = 144
mpl_styles = {
    'figure.figsize': (6, 4),
    # Up the default resolution for figures.
    'figure.dpi': dpi,
    'savefig.dpi': dpi,
} """

#sns.set_theme(context='paper')
#plt.rcParams.update(mpl_styles)

df = sns.load_dataset('taxis')
df.head()

# Convert the pickup time to datetime and create a new column truncated to day.
df['pickup'] = pd.to_datetime(df.pickup)
df['pickup_date'] = pd.to_datetime(df.pickup.dt.date)
# Altair can't handle more than 5k rows so we truncate the data.
df = df.loc[df['pickup_date'] >= '2019-03-01'][:5000]

# We also create a grouped version, with calculated mean and standard deviation.
df_grouped = (
    df[['pickup_date', 'fare']].groupby(['pickup_date'])
    .agg(['mean', 'std', 'count'])
)
df_grouped = df_grouped.droplevel(axis=1, level=0).reset_index()
# Calculate a confidence interval as well.
df_grouped['ci'] = 1.96 * df_grouped['std'] / np.sqrt(df_grouped['count'])
print(df_grouped['mean'])
df_grouped['ci_lower'] = df_grouped['mean'] - df_grouped['ci']
df_grouped['ci_upper'] = df_grouped['mean'] + df_grouped['ci']
df_grouped.head()

fig, ax = plt.subplots()
x = df_grouped['pickup_date']
ax.plot(x, df_grouped['mean'])
ax.fill_between(
    x, df_grouped['ci_lower'], df_grouped['ci_upper'], color='b', alpha=.15)
#ax.set_ylim(ymin=0)
ax.set_title('Avg Taxi Fare by Date')
fig.autofmt_xdate(rotation=45)
plt.show()