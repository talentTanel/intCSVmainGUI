import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# set path to folder containing CSV files
folder_path = 'C:/Users/Tanel/Desktop/kool/Internship/main/intCSVmainGUI/Groups/Scenario_1_Injection_Middle_66P/CSVTEST'

# create an empty list to store all the dataframes
df_list = []

# loop through all CSV files in the folder and append their dataframes to df_list
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)
        df = pd.read_csv(file_path)
        df['filename'] = filename  # add a column to identify the filename
        df_list.append(df)

# combine all dataframes in df_list into one large dataframe
combined_df = pd.concat(df_list)

scaler = MinMaxScaler()
combined_df['Time [ms]'] = scaler.fit_transform(combined_df[['Time [ms]']])

# calculate the mean and standard deviation of the pressure values at every time point using groupby
grouped_df = combined_df.groupby('Time [ms]')['PL [hPa]'].agg(['mean', 'std'])
grouped_df.reset_index(inplace=True)  # reset the index to make Time [ms] a column again
median_std = grouped_df['std'].median()
grouped_df['std'].fillna(median_std, inplace=True)
# add a rolling mean to the grouped dataframe
window_size = 100  # set the window size for the rolling mean
grouped_df['rolling_mean'] = grouped_df['mean'].rolling(window_size, center=True).mean()
grouped_df['rolling_std'] = grouped_df['std'].rolling(window_size, center=True).std()
grouped_df['lower'] = grouped_df['mean']-grouped_df['std']
grouped_df['upper'] = grouped_df['mean']+grouped_df['std']
# plot the data using matplotlib
plt.figure()

#plt.title('Pressure vs. Time')
plt.xlabel('Normalised time')
plt.ylabel('Pressure (mbar)')

# plot the mean line and confidence interval using the grouped dataframe
plt.fill_between(grouped_df['Time [ms]'], grouped_df['lower'], grouped_df['upper'], color='red', alpha=0.2)

for filename in set(combined_df['filename']):
    # get the data for the current file and plot it as a line
    file_data = combined_df[combined_df['filename'] == filename]
    plt.plot(file_data['Time [ms]'], file_data['PL [hPa]'], color="gray", linewidth=0.5)
    
plt.plot(grouped_df['Time [ms]'], grouped_df['rolling_mean'], color='r', alpha=1, linewidth=5)
plt.show()
