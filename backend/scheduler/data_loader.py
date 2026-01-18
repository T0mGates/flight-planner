import numpy as np
import pandas as pd
import os

# Assuming these helpers remain in your backend structure
from backend.scheduler.constants import EARTH_RADIUS_NM, FEET_TO_NM, TRANSLATION, PLANE_TYPE_MAP
from backend.scheduler.helpers import haversine_vectorized
from backend.scheduler.lookups import create_flight_constraints

def load_data(file_path: str) -> pd.DataFrame:
    """
    Load flight data from a JSON file and perform initial transformations.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    abs_path = os.path.join(base_dir, file_path)
    df = pd.read_json(abs_path)
    df.columns = [col.replace(' ', '_') for col in df.columns]

    # Map airport codes to lat/lon and plane types to standard types
    df['arrival_airport'] = df['arrival_airport'].map(TRANSLATION)
    df['departure_airport'] = df['departure_airport'].map(TRANSLATION)
    df['Plane_type'] = df['Plane_type'].map(PLANE_TYPE_MAP)

    return df

def get_ecef_from_coord(coord_str: str, altitude_ft: float) -> np.ndarray:
    """
    Converts a coordinate string (e.g., '45.0N/75.0W') and altitude to 
    Earth-Centered, Earth-Fixed (ECEF) Cartesian coordinates.
    """
    lat_str, lon_str = coord_str.split('/')
    
    def parse_coord(val: str) -> float:
        v = float(val[:-1])
        return v if val[-1] in 'NE' else -v
    
    lat = np.radians(parse_coord(lat_str))
    lon = np.radians(parse_coord(lon_str))
    
    # Radius = Earth Radius + Altitude (converted to Nautical Miles)
    R = EARTH_RADIUS_NM + (altitude_ft * FEET_TO_NM)
    
    return np.array([
        R * np.cos(lat) * np.cos(lon), # X
        R * np.cos(lat) * np.sin(lon), # Y
        R * np.sin(lat)                # Z
    ])

def generate_flight_schedule(file_path: str) -> pd.DataFrame:
    """
    Full pipeline to load raw flight JSON and transform it into a 
    4D-resolved ready format with ECEF coordinates and time windows.
    """
    # 1. Load Data
    df = load_data(file_path)

    # 2. Flatten Route into Waypoint Segments
    waypoints_list = []
    for _, row in df.iterrows():
        # Build full path: Start -> Waypoints -> End
        route_points = [row['departure_airport']] + row['route'].split() + [row['arrival_airport']]
        for i in range(len(route_points) - 1):
            waypoints_list.append({
                'segment_number': i + 1,
                'ACID': row['ACID'],
                'Plane_type': row['Plane_type'],
                'from': route_points[i],
                'to': route_points[i + 1],
                'passengers': row.get('passengers', 200),
                'departure_time_orig': row['departure_time']
            })
    
    wp_df = pd.DataFrame(waypoints_list)

    # 3. Integrate Constraints (Altitude/Speed)
    alt_constraints, speed_constraints = create_flight_constraints()
    
    # Merge Airplane Specs
    wp_df = wp_df.merge(alt_constraints, left_on='Plane_type', right_on='Aircraft_Type', how='left')
    wp_df = wp_df.merge(speed_constraints, left_on='Plane_type', right_on='Aircraft_Type', how='left', suffixes=('', '_s'))

    # 4. Calculate Physics (Distances & Durations)
    wp_df['travel_distance_nm'] = haversine_vectorized(wp_df)
    
    # Duration = Distance / Speed (converted to seconds)
    wp_df['duration_sec'] = (wp_df['travel_distance_nm'] / wp_df['Max_cruise_Speed_knots']) * 3600
    
    # Set default altitude to minimum available for safety baseline
    wp_df['chosen_altitude_ft'] = wp_df['Min_altitude_ft']

    # 5. Calculate Temporal Windows (Departure/Arrival per segment)
    wp_df['departure_time_dt'] = pd.to_datetime(wp_df['departure_time_orig'], unit='s')
    wp_df = wp_df.sort_values(['ACID', 'segment_number'])
    
    # Calculate cumulative time offset per flight
    wp_df['cum_duration'] = wp_df.groupby('ACID')['duration_sec'].cumsum()
    
    wp_df['estimated_arrival_time'] = wp_df['departure_time_dt'] + pd.to_timedelta(wp_df['cum_duration'], unit='s')
    wp_df['estimated_departure_time'] = wp_df['estimated_arrival_time'] - pd.to_timedelta(wp_df['duration_sec'], unit='s')

    # 6. Spatial Conversion (ECEF)
    wp_df['from_ECEF'] = wp_df.apply(lambda r: get_ecef_from_coord(r['from'], r['chosen_altitude_ft']), axis=1)
    wp_df['to_ECEF'] = wp_df.apply(lambda r: get_ecef_from_coord(r['to'], r['chosen_altitude_ft']), axis=1)

    # 7. Clean up and Return Required Columns
    target_cols = [
        'segment_number', 'ACID', 'from_ECEF', 'to_ECEF', 'travel_distance_nm',
        'Min_altitude_ft', 'Max_altitude_ft', 'Optimal_altitude_min', 'Optimal_altitude_max',
        'Max_cruise_Speed_knots', 'Min_cruise_Speed_knots', 'Min_Speed_knots', 'Max_Speed_knots',
        'estimated_departure_time', 'estimated_arrival_time', 'chosen_altitude_ft', 'passengers'
    ]
    
    return wp_df[target_cols].sort_values('estimated_departure_time')

# Usage
if __name__ == "__main__":
    flight_arrival_times = generate_flight_schedule('canadian_flights_1000.json')
    print(flight_arrival_times.head())