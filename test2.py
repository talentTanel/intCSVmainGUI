import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

path = 'C:/Users/Tanel/Desktop/kool/Internship/main/intCSVmainGUI/Groups/Scenario_1_Injection_Middle_66P/CSVTEST'

dfTemp = []
for filename in os.listdir(path): # making a list of all files in folder and reads all data into one dataframe
    if filename.endswith('.csv'):
        filePath = os.path.join(path, filename)
        df = pd.read_csv(filePath)
        df['filename'] = filename
        dfTemp.append(df)
df_combined = pd.concat(dfTemp)

# Normalize time from 0 to 1
df_combined['Time [ms]'] = (df_combined['Time [ms]']-np.min(df_combined['Time [ms]']))/(np.max(df_combined['Time [ms]'])-np.min(df_combined['Time [ms]']))


df_grouped = df_combined.groupby('Time [ms]')['PL [hPa]'].agg(['mean', 'std']) # get mean & standard deviation
df_grouped.reset_index(inplace=True)  # reset the index to make Time [ms] a column again
median_std = df_grouped['std'].median()
df_grouped['std'].fillna(median_std, inplace=True) # changing NaN std values to median std

# Smoothing out the mean into a rolling mean. Otherwise it looks bad on graph
window_size = 100
df_grouped['rolling_mean'] = df_grouped['mean'].rolling(window_size, center=True).mean()
df_grouped['lower'] = df_grouped['mean']-df_grouped['std']
df_grouped['upper'] = df_grouped['mean']+df_grouped['std']


plt.figure()
plt.title('95% Confidence')
plt.xlabel('Normalised time')
plt.ylabel('Pressure (mbar)')

plt.fill_between(df_grouped['Time [ms]'], df_grouped['lower'], df_grouped['upper'], color='red', alpha=0.2)

# separate plots for each file
for filename in set(df_combined['filename']):
    file_data = df_combined[df_combined['filename'] == filename]
    plt.plot(file_data['Time [ms]'], file_data['PL [hPa]'], color="gray", linewidth=0.5)
    
plt.plot(df_grouped['Time [ms]'], df_grouped['rolling_mean'], color='r', alpha=1, linewidth=5)
plt.show()
