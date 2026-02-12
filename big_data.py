import pandas as pd

# Load a large dataset (example: CSV file)
# Assuming you have a big CSV file, e.g., 'large_data.csv'
df = pd.read_csv('large_data.csv')


# Example: Group by a column and aggregate
grouped = df.groupby('column_name').sum()
print(grouped)