import pandas as pd
import numpy as np

def haversine_vectorized(df: pd.DataFrame) -> pd.Series:
    
    # Helper to parse coordinate string to float (e.g., '49.19N' -> 49.19, '123.18W' -> -123.18)
    def parse_coord(coord):
        val = float(coord[:-1])
        return val if coord[-1] in 'NE' else -val

    # Split 'from' and 'to' into latitude and longitude columns
    from_lat = df['from'].str.split('/', expand=True)[0].apply(parse_coord)
    from_lon = df['from'].str.split('/', expand=True)[1].apply(parse_coord)
    to_lat = df['to'].str.split('/', expand=True)[0].apply(parse_coord)
    to_lon = df['to'].str.split('/', expand=True)[1].apply(parse_coord)

    # Convert degrees to radians
    lat1 = np.radians(from_lat)
    lon1 = np.radians(from_lon)
    lat2 = np.radians(to_lat)
    lon2 = np.radians(to_lon)
        
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    R = 3440.065  # nautical miles
    distances = R * c
    return pd.Series(distances)