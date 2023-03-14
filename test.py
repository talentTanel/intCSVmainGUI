import numpy as np

# create a numpy array with string and 3 floats
data = np.array([['string1', 1.2, 2.3, 3.4],
                 ['string2', 4.5, 5.6, 6.7]])

# specify the file name and delimiter
file_name = 'output.csv'
delimiter = ','

# use savetxt to write the data to the CSV file
np.savetxt(file_name, data, delimiter=delimiter, fmt='%s,%.1f,%.1f,%.1f', encoding='utf-8')
