def query_api():
    """
    This function queries the NREL NSRDB API to request hourly solar resource data (GHI, DNI, DHI, humidity, zenith angle) 
    for a set of Texas cities across the years 2021-2023.

    The API may respond in one of two ways:
    - If the data needs to be prepared, a download URL is returned. This URL is saved to a dictionary (`download_url_dict`)
    for later use.
    - If the data is already prepared and ready for download, a ZIP file is returned immediately. These ZIPs are saved to
    the `nsrdb_zip_cache/` directory for later extraction.

    After all requests are made, the script saves the dictionary of download URLs as `download_url_dict.json`.
    """

    ### Import Libraries
    import requests
    import time
    import json
    import os


    ### Define Parameters
    API_KEY = os.environ.get('API_KEY')
    URL = f"https://developer.nrel.gov/api/nsrdb/v2/solar/nsrdb-GOES-conus-v4-0-0-download.json?api_key={API_KEY}"
    ATTRIBUTES = 'ghi,dni,dhi,solar_zenith_angle,relative_humidity'
    YEARS = ['2021', '2022', '2023']
    EMAIL = 'kmundey@utexas.edu'

    # These are the cities we will extract data for
    cities_by_region = {
        "south": {
            "McAllen": (26, -98),
            "Austin": (30, -98),
            "SanAntonio": (29, -98),
            "Laredo": (28, -100),
            "CorpusChristi": (28, -97)
        },
        "north": {
            "Waco": (32, -97),
            "Dallas": (33, -97),
            "Tyler": (32, -95)
        },
        "west": {
            "Amarillo": (35, -102),
            "Lubbock": (34, -102),
            "Midland": (32, -102),
            "SanAngelo": (31, -100),
            "WichitaFalls": (34, -98),
            "Alpine": (30, -104)
        },
        "east": {
            "Houston": (30, -95)
        }
    }

    # Initialize a dictionary to store the Download URLs in
    download_url_dict = {}

    ### Define method to add URL to dictionary
    def add_to_dict(response, download_url_dict):
        result = response.json()
        download_url = result['outputs']['downloadUrl']
        download_url_dict[year][region][city] = download_url
        print(f"Queued: {result['outputs']['message']}\n")


    ### Make POST requests to the NREL API

    # Iterate through each year
    for year in YEARS:
        print(f"--- YEAR {year} ---")
        download_url_dict[year] = {}

        # Iterate through each region
        for region, cities in cities_by_region.items():
            download_url_dict[year][region] = {}

            # Iterate through each city and send POST request for data Download URL
            for city, (lat, lon) in cities.items():
                print(f"Requesting {region}: {city} ({year})...")

                WKT = f'POINT({lon} {lat})'
                
                payload = f'api_key={API_KEY}&attributes={ATTRIBUTES}&names={year}&interval=60&email={EMAIL}&wkt={WKT}'

                headers = {
                'content-type': 'application/x-www-form-urlencoded',
                'cache-control': 'no-cache'
                }

                # Unpack the response
                try:
                    response = requests.post(URL, data=payload, headers=headers)
                    content_type = response.headers.get('Content-Type', '')

                    # If the response is successful
                    if response.status_code == 200:
                        
                        # If the response is a Download URL, add to URL dictionary
                        if 'application/json' in content_type:
                            add_to_dict(response, download_url_dict)
                        
                        else:
                            print(f"Unexpected content type for {city}: {content_type}\n{response.text[:300]}\n") 
                    
                    else:
                        print(f"{city} failed — status code: {response.status_code}\n{response.text[:300]}\n")

                except Exception as e:
                    print(f"Exception for {city}: {e}\n")
                
                time.sleep(2)  # rate limit

            print()
        print()



    ### After sucessful extraction of URLs, save to JSON file

    # Define path
    json_path = 'download_url_dict.json'

    # Save to JSON
    with open(json_path, 'w') as f:
        json.dump(download_url_dict, f, indent=2)

    print("Done! Saved download_url_dict.json\n")


def process_urls():
    """
    This function reads a dictionary of pre-fetched NSRDB download URLs (from `download_url_dict.json`),
    downloads each ZIP file, extracts the `.csv` inside, and stores it using the format:

        nsrdb_<year>_<region>_<city>.csv

    If a URL is missing or an error occurs during download/extraction, it is reported but skipped.
    """

    ### Import Libraries
    import os
    import json
    import requests
    import zipfile
    from io import BytesIO

    # Load the Download URL dictionary
    with open('download_url_dict.json', 'r') as f:
        download_url_dict = json.load(f)

    # Base directory to store all data
    base_dir = 'raw_nsrdb_data'
    os.makedirs(base_dir, exist_ok=True)

    # Loop through each year
    for year, regions in download_url_dict.items():
        print(f'--- YEAR {year} ---')

        # Create a subfolder for the year
        year_dir = os.path.join(base_dir, f'nsrdb_{year}')
        os.makedirs(year_dir, exist_ok=True)

        # Loop through each region and download each city's data
        for region, cities in regions.items():
            for city, url in cities.items():
                
                # Create filepath
                if url:
                    filename = f'nsrdb_{year}_{region}_{city}.csv'
                    filepath = os.path.join(year_dir, filename)
                    
                    try:
                        # Download the file from the URL
                        print(f'Downloading {filename}\n')
                        r = requests.get(url, stream=True)
                        r.raise_for_status()

                        # Unzip and extract the file
                        with zipfile.ZipFile(BytesIO(r.content)) as z:
                            zipped_file = z.namelist()[0]
                            with z.open(zipped_file) as inner_file, open(filepath, 'wb') as out_file:
                                out_file.write(inner_file.read())
                            
                    except Exception as e:
                        print(f'Error downloading {filename}: {e}\n')
                
                else:
                    print(f'No URL for {city}, {region}, {year}\n')
            print()
        print()

    print('Finished processing URLs.\n')


def aggregate_one_year_by_city(year):
    """
    Combines city-level NSRDB Excel files for a given year into a single wide-format DataFrame.
    Each column is {city}_{feature}, and the index is a timestamp in YYYY-MM-DD-HH format.

    Parameters:
        year (str): Year to process, e.g., "2021"

    Returns:
        pd.DataFrame: Wide-format DataFrame with hourly rows and {city}_{feature} columns
    """
    import pandas as pd 
    import os

    city_dfs = []
    year_path = f'raw_nsrdb_data\\nsrdb_{year}'

    for filename in os.listdir(year_path):
        
        filepath = os.path.join(year_path, filename)

        # Format: nsrdb_year_region_city.csv
        parts = filename.split('_')
        city = parts[3].lower()

        # Read Excel file
        df = pd.read_csv(filepath, skiprows=2)

        # Create timestamp column
        df['timestamp'] = pd.to_datetime({
                'year': df['Year'],
                'month': df['Month'],
                'day': df['Day'],
                'hour': df['Hour']
            })

        df.set_index('timestamp', inplace=True)

        # Drop time columns
        df.drop(columns=['Year', 'Month', 'Day', 'Hour', 'Minute'], inplace=True, errors='ignore')
        
        # Rename columns to {city}_{feature}
        df.columns = [f"{city[:-4]}_{col.lower().replace(' ', '_')}" for col in df.columns]

        city_dfs.append(df)

    # Merge all city dataframes on timestamp index
    combined_df = pd.concat(city_dfs, axis=1)

    # Sort index (just in case)
    combined_df.sort_index(inplace=True)

    return combined_df


def aggregate_by_region(city_df):
    """
    Describe function
    """

    import pandas as pd
    
    # Maps cities to their respective regions
    regions_dict = {
        "south": ["mcallen", "austin", "sanantonio", "laredo", "corpuschristi"],
        "north": ["waco", "dallas", "tyler"],
        "west": ["amarillo", "lubbock", "midland", "sanangelo", "wichitafalls", "alpine"],
        "east": ["houston"]
    }
    
    # Initialize dict to hold region-level dataframes
    region_df_dict = {}

    # Loop through each region
    for region, cities in regions_dict.items():
        
        # Get columns that belong to the cities in this region
        region_cols = [col for col in city_df.columns if any(col.startswith(city) for city in cities)]
        
        # Subset dataframe for those columns
        region_df = city_df[region_cols]
        
        # Average across cities for each feature (grouping by the solar attribute)
        grouped = region_df.T.groupby(lambda col: col.split("_", 1)[1]).mean().round(3).T
        
        # Rename columns to region_feature
        grouped.columns = [f"{feature}_{region}" for feature in grouped.columns]
        
        # Store result in dictionary
        region_df_dict[region] = grouped

    # Combine all region-level dataframes
    regions_df = pd.concat(region_df_dict.values(), axis=1)

    # Set index to the timestamp
    regions_df.index = city_df.index
    regions_df.index.name = 'timestamp'

    return regions_df