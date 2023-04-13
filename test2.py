import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import MinMaxScaler

path = 'C:/Users/Tanel/Desktop/kool/Internship/main/intCSVmainGUI/Groups/Scenario_1_Injection_Middle_66P/CSVTEST'
df_list = []

for filename in os.listdir(path):
    if filename.endswith('.csv'):
        file_path = os.path.join(path, filename)
        df = pd.read_csv(file_path)
        df['filename'] = filename  # add a column to identify the filename
        df_list.append(df)
combined_df = pd.concat(df_list)

scaler = MinMaxScaler()
combined_df['Time [ms]'] = scaler.fit_transform(combined_df[['Time [ms]']])

# mean & std
grouped_df = combined_df.groupby('Time [ms]')['PL [hPa]'].agg(['mean', 'std'])
grouped_df.reset_index(inplace=True)  # reset the index to make Time [ms] a column again
median_std = grouped_df['std'].median()
grouped_df['std'].fillna(median_std, inplace=True) # changing NaN std values to median std

# rolling mean
window_size = 100
grouped_df['rolling_mean'] = grouped_df['mean'].rolling(window_size, center=True).mean()
grouped_df['rolling_std'] = grouped_df['std'].rolling(window_size, center=True).std()
grouped_df['lower'] = grouped_df['mean']-grouped_df['std']
grouped_df['upper'] = grouped_df['mean']+grouped_df['std']


plt.figure()
plt.title('95% Confidence')
plt.xlabel('Normalised time')
plt.ylabel('Pressure (mbar)')

plt.fill_between(grouped_df['Time [ms]'], grouped_df['lower'], grouped_df['upper'], color='red', alpha=0.2)

# separate plots for each file
for filename in set(combined_df['filename']):
    file_data = combined_df[combined_df['filename'] == filename]
    plt.plot(file_data['Time [ms]'], file_data['PL [hPa]'], color="gray", linewidth=0.5)
    
plt.plot(grouped_df['Time [ms]'], grouped_df['rolling_mean'], color='r', alpha=1, linewidth=5)
plt.show()
