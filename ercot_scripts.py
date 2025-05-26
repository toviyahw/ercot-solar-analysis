import os
import zipfile
import pandas as pd
from io import BytesIO
from datetime import timedelta

def extract_zips(outer_file):

    # List to collect all data
    all_data = []

    # Loop over each top-level zip file
    for filename in os.listdir(outer_file):
        if filename.endswith(".zip"):
            zip_path = os.path.join(outer_file, filename)
            
            with zipfile.ZipFile(zip_path, 'r') as top_zip:  # Open top-level ZIP
                
                for inner_file in top_zip.namelist():

                    if inner_file.endswith(".zip"):
                        nested_zip_bytes = BytesIO(top_zip.read(inner_file))  # Read nested zip into memory

                        with zipfile.ZipFile(nested_zip_bytes, 'r') as nested_zip:
                            
                            for csv_name in nested_zip.namelist():
                                if csv_name.endswith(".csv"):
                                    with nested_zip.open(csv_name) as csv_file:
                                        try:
                                            df = pd.read_csv(csv_file, skiprows=1, nrows=48, header=None)
                                            all_data.append(df)
                                        except Exception as e:
                                            print(f"Failed to read {csv_name} in {filename}: {e}")
                    
                    # It's a CSV directly in the top-level zip
                    elif inner_file.lower().endswith(".csv"): 
                        with top_zip.open(inner_file) as csv_file:
                            try:
                                df = pd.read_csv(csv_file, skiprows=1, nrows=48, header=None)
                                all_data.append(df)
                            except Exception as e:
                                print(f"Failed to read {inner_file} in {filename}: {e}")
    
    return all_data


def create_timestamp(df):
    """
    Creates a timeseries column and assigns it to the index.
    """

    # Convert 'date' column to datetime object
    df['date'] = pd.to_datetime(df['date'], format='%m/%d/%Y')

    # Add 'hour' to 'date'
    df['timestamp'] = df['date'] + pd.to_timedelta(df['hour'], unit='h')

    # Set timestamp as index
    df.set_index('timestamp', inplace=True)

    df = df.sort_index()

    # Drop columns not needed
    df.drop(columns=['date', 'hour'], inplace=True, errors='ignore')    

    return df


def extract_wind():

    all_data = extract_zips("wind_generation_zips")

    cols = ['date', 'hour', 'wind_system', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'wind_coast', 'x', 'x', 'x', 
            'wind_south', 'x', 'x', 'x', 'wind_west', 'x', 'x', 'x', 'wind_north', 'x', 'x', 'x', 'x']

    # Combine all 48-row chunks into one DataFrame
    df = pd.concat(all_data, ignore_index=True)

    # Drop unnecessary columns
    df.columns = cols
    df = df.loc[:, df.columns != 'x']

    # Remove any duplicates
    df = df.drop_duplicates()

    # Create timeseries index column
    final_df = create_timestamp(df)

    # Stop data at 2023-12-31
    final_df = final_df[final_df.index <= pd.to_datetime('2023-12-31 23:00:00')]


    print("Complied ERCOT Wind Generation data into a DataFrame")

    return final_df

def extract_solar():

    all_data = extract_zips("solar_generation_zips")

    cols = ['date', 'hour', 'solar_system', 'x', 'x', 'x', 'solar_centerwest', 'x', 'x', 'x', 'solar_northwest', 
            'x', 'x', 'x', 'solar_farwest', 'x', 'x', 'x', 'solar_fareast', 'x', 'x', 'x', 'solar_southeast', 
            'x', 'x', 'x', 'solar_centereast', 'x', 'x', 'x', 'x']

    # Combine all 48-row chunks into one DataFrame
    df = pd.concat(all_data, ignore_index=True)

    # Drop unnecessary columns
    df.columns = cols
    df = df.loc[:, df.columns != 'x']

    # Create timeseries index column
    final_df = create_timestamp(df)

    # Stop data at 2023-12-31
    final_df = final_df[final_df.index <= pd.to_datetime('2023-12-31 23:00:00')]

    print("Complied ERCOT Solar Generation data into a DataFrame")

    return final_df


def shift_timestamps(df, col):
    
    def fix_and_shift(dt_str):
        if '24:00' in dt_str:
            # Replace 24:00 with 00:00 and go to next day
            base = pd.to_datetime(dt_str.replace('24:00', '00:00'))
            return base + timedelta(days=1) - timedelta(hours=1)
        else:
            return pd.to_datetime(dt_str) - timedelta(hours=1)
    
    df['timestamp'] = df[col].apply(fix_and_shift)
    
    return df


def extract_load(filepaths):
    
    all_data = []
    cols = ['timestamp', 'coast', 'east', 'farwest', 'north', 'northcentral', 'south', 'southcentral', 'west', 'system']

    for path in filepaths:
        df = pd.read_csv(path)
        all_data.append(df)

    # Combine into one DataFrame
    df = pd.concat(all_data, ignore_index=True)

    # Rename columns
    df.columns = cols

    # Create timeseries index column
    df = shift_timestamps(df, 'timestamp')

    # Create timeseries index column
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed', dayfirst=False)
    df.set_index('timestamp', inplace=True)


    return df


    