import pandas as pd
import os

from backend.scheduler.constants import TRANSLATION, PLANE_TYPE_MAP
from backend.scheduler.helpers import haversine_vectorized
from backend.scheduler.lookups import create_flight_constraints

pd.set_option('display.max_columns', None)

def load_data(file_path: str) -> pd.DataFrame | None:
    """
    Load data from a JSON file into a pandas DataFrame.

    Args:
        file_path (str): Path to the JSON file, relative to this script.

    Returns:
        pd.DataFrame or None: Loaded DataFrame or None if error occurs.
    """
    try:
        # Get absolute path relative to this file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        abs_path = os.path.join(base_dir, file_path)
        print(f"Loading data from: {abs_path}")
        data = pd.read_json(abs_path)
        data.columns = [col.replace(' ', '_') for col in data.columns]
        return data
    except Exception as e:
        print(f"An error occurred while loading the data: {e}")
        return None

def map_to_standard_formats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform arrival and departure airports using TRANSLATION dictionary.

    Args:
        df (pd.DataFrame): DataFrame containing flight data.

    Returns:
        pd.DataFrame: DataFrame with transformed airport codes.
    """
    try:
        df['arrival_airport'] = df['arrival_airport'].map(TRANSLATION)
        df['departure_airport'] = df['departure_airport'].map(TRANSLATION)
        df['Plane_type'] = df['Plane_type'].map(PLANE_TYPE_MAP)
        return df
    except Exception as e:
        print(f"An error occurred while transforming the airports: {e}")
        return df

def create_flight_waypoints(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create waypoints for each flight from departure to arrival airport, 
    including all route waypoints in between.

    Args:
        df (pd.DataFrame): DataFrame containing flight data.

    Returns:
        pd.DataFrame: DataFrame with flight waypoints.
    """
    try:
        waypoints_data = []
        idx = 0
        for _, row in df.iterrows():
            route_points = [row['departure_airport']] + row['route'].split() + [row['arrival_airport']]
            depends = None
            for i in range(len(route_points) - 1):
                waypoints_data.append({
                    'index': idx,
                    'depends_on': depends,
                    'flight_id': row['ACID'],
                    'from': route_points[i],
                    'to': route_points[i + 1]
                })
                depends = idx
                idx += 1
        waypoints_df = pd.DataFrame(waypoints_data)
        return waypoints_df
    except Exception as e:
        print(f"An error occurred while creating flight waypoints: {e}")
        return pd.DataFrame()

def create_flight_lookup(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a lookup table for flights with non-changing attributes.

    Args:
        df (pd.DataFrame): DataFrame containing flight data.

    Returns:
        pd.DataFrame: Lookup DataFrame with static flight attributes.
    """
    try:
        lookup_df = df[['ACID', 'Plane_type', 'departure_time', 'is_cargo', 'passengers']].drop_duplicates().reset_index(drop=True)
        return lookup_df
    except Exception as e:
        print(f"An error occurred while creating flight lookup table: {e}")
        return pd.DataFrame()
    
def calculate_travel_distances(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate travel distances between each waypoint segment.

    Args:
        df (pd.DataFrame): DataFrame containing flight data.

    Returns:
        pd.DataFrame: DataFrame with travel distances.
    """
    try:
        # Haversine formula vectorized
        distances = haversine_vectorized(df)

        df['travel_distance_nm'] = distances
        return df
    except Exception as e:
        print(f"An error occurred while calculating travel distances: {e}")
        return df

if __name__ == "__main__":
    data_file = 'canadian_flights_1000.json'
    df = load_data(data_file)

    df = map_to_standard_formats(df)
    waypoints_df = create_flight_waypoints(df)
    lookup_df = create_flight_lookup(df)

    altitude_df, speed_df = create_flight_constraints(lookup_df)
    waypoints_df = calculate_travel_distances(waypoints_df)

    print("Flight DataFrame:")
    print(df)
    print("\nFlight Waypoints:")
    print(waypoints_df)
    print("\nFlight Lookup:")
    print(lookup_df)
    print("\nAltitude Constraints:")
    print(altitude_df)
    print("\nSpeed Constraints:")
    print(speed_df)
    
    

