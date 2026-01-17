import numpy as np
import pandas as pd
import os

from backend.scheduler.constants import EARTH_RADIUS_NM, FEET_TO_NM, TRANSLATION, PLANE_TYPE_MAP
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
        for _, row in df.iterrows():
            route_points = [row['departure_airport']] + row['route'].split() + [row['arrival_airport']]
            seg_num = 1
            for i in range(len(route_points) - 1):
                waypoints_data.append({
                    'segment_number': seg_num,
                    'ACID': row['ACID'],
                    'from': route_points[i],
                    'to': route_points[i + 1]
                })
                seg_num += 1
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
    
def calculate_flight_duration(df: pd.DataFrame, flight_lookup: pd.DataFrame, airplane_lookup: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate estimated flight duration based on distance and airplane speed.

    Args:
        df (pd.DataFrame): DataFrame containing flight waypoints with distances.
        flight_lookup (pd.DataFrame): Lookup DataFrame with flight attributes.
        airplane_lookup (pd.DataFrame): Lookup DataFrame with airplane speeds.

    Returns:
        pd.DataFrame: DataFrame with estimated flight durations.
    """
    try:
        merged_df = df.merge(flight_lookup[['ACID', 'Plane_type']], left_on='ACID', right_on='ACID', how='left')
        merged_df = merged_df.merge(airplane_lookup[['Aircraft_Type', 'Max_cruise_Speed_knots']], left_on='Plane_type', right_on='Aircraft_Type', how='left')
        
        merged_df['estimated_duration_seconds'] = merged_df['travel_distance_nm'] / merged_df['Max_cruise_Speed_knots'] * 3600
        return merged_df
    except Exception as e:
        print(f"An error occurred while calculating flight durations: {e}")
        return df
    
def calculate_altitude(df: pd.DataFrame, flight_lookup: pd.DataFrame, airplane_lookup: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate optimal altitude for each flight segment.

    Args:
        df (pd.DataFrame): DataFrame containing flight waypoints.
        flight_lookup (pd.DataFrame): Lookup DataFrame with flight attributes.
        airplane_lookup (pd.DataFrame): Lookup DataFrame with airplane altitudes.

    Returns:
        pd.DataFrame: DataFrame with chosen altitudes.
    """
    try:
        merged_df = df.merge(airplane_lookup[['Aircraft_Type', 'Min_altitude_ft', 'Max_altitude_ft']], on='Aircraft_Type', how='left')
        
        # Choose random altitude within optimal range for simplicity
        merged_df['chosen_altitude_ft'] = merged_df.apply(
            lambda row: np.random.randint(row['Min_altitude_ft'], row['Max_altitude_ft'] + 1),
            axis=1
        )
        
        return merged_df
    except Exception as e:
        print(f"An error occurred while calculating altitudes: {e}")
        return df
    
def calculate_waypoint_times(df: pd.DataFrame, lookup_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate estimated arrival times at each waypoint based on departure time and segment durations.

    Args:
        df (pd.DataFrame): DataFrame containing flight waypoints with estimated durations.
        lookup_df (pd.DataFrame): Lookup DataFrame with flight departure times.
    Returns:
        pd.DataFrame: DataFrame with estimated waypoint arrival times.
    """
    try:
        df = df.merge(lookup_df[['ACID', 'departure_time']], on='ACID', how='left')
        df = df.sort_values(by=['ACID', 'segment_number'])

        # Ensure departure_time is datetime
        df['departure_time'] = pd.to_datetime(df['departure_time'], unit='s')

        # Calculate cumulative duration per flight
        df = df.sort_values(by=['ACID', 'segment_number'], ascending=[True, True])
        df['cumulative_duration'] = df.groupby('ACID')['estimated_duration_seconds'].cumsum()
        
        # Estimated arrival time = departure_time + cumulative_duration (in seconds)
        df['estimated_arrival_time'] = df['departure_time'] + pd.to_timedelta(df['cumulative_duration'], unit='s')
        df['estimated_departure_time'] = df['estimated_arrival_time'] - pd.to_timedelta(df['estimated_duration_seconds'], unit='s')
        
        # Drop helper columns
        df = df.drop(columns=['departure_time', 'cumulative_duration'])
        
        # sort by estimated arrival time
        df = df.sort_values(by=['estimated_departure_time'])

        return df
    except Exception as e:
        print(f"An error occurred while calculating waypoint times: {e}")
        return df

def get_3d_position(lat, lon, alt_ft):
    """
    Convert lat/lon/altitude to 3D Cartesian coordinates.
    Using Earth-centered Earth-fixed (ECEF) coordinate system.
    
    Args:
        lat, lon: in radians
        alt_ft: altitude in feet
    
    Returns:
        np.array: [x, y, z] in nautical miles
    """
    # Earth radius in nautical miles + altitude
    R = EARTH_RADIUS_NM + alt_ft * FEET_TO_NM  # Convert feet to nautical miles
    
    x = R * np.cos(lat) * np.cos(lon)
    y = R * np.cos(lat) * np.sin(lon)
    z = R * np.sin(lat)
    
    return np.array([x, y, z])


def calculate_cpa_analytical(row1: pd.Series, row2: pd.Series, horizontal_threshold_nm: int) -> tuple:
    """
    Analytically calculate the closest point of approach (CPA) between two aircraft.
    
    Models each aircraft as traveling linearly in 3D space (including altitude).
    Position as function of time: P(t) = P0 + V * (t - t0)
    Distance squared: D²(t) = ||P1(t) - P2(t)||²
    
    To minimize D²(t), take derivative and set to 0:
    d/dt[D²(t)] = 0
    
    This gives us a closed-form solution for the time of CPA.
    
    Args:
        row1, row2: Series with segment info
        horizontal_threshold_nm: Horizontal distance threshold in nautical miles
    
    Returns:
        tuple: (min_distance_nm, cpa_time_timestamp, is_valid)
    """    
    # Convert to radians
    lat1_start, lon1_start = row1['from_lat_rad'], row1['from_lon_rad']
    lat1_end, lon1_end = row1['to_lat_rad'], row1['to_lon_rad']
    lat2_start, lon2_start = row2['from_lat_rad'], row2['from_lon_rad']
    lat2_end, lon2_end = row2['to_lat_rad'], row2['to_lon_rad']
    
    # Get altitudes (use chosen altitude for calculation)
    alt1 = row1['chosen_altitude_ft']
    alt2 = row2['chosen_altitude_ft']
    
    # Get time parameters (in seconds since epoch)
    t1_start = row1['estimated_departure_time'].timestamp()
    t1_end = row1['estimated_arrival_time'].timestamp()
    t2_start = row2['estimated_departure_time'].timestamp()
    t2_end = row2['estimated_arrival_time'].timestamp()

    # Check for time overlap
    overlap_start = max(t1_start, t2_start)
    overlap_end = min(t1_end, t2_end)
    
    if overlap_start > overlap_end:
        return float('inf'), None, False
    
    # Convert to 3D positions
    P1_start = get_3d_position(lat1_start, lon1_start, alt1)
    P1_end = get_3d_position(lat1_end, lon1_end, alt1)
    P2_start = get_3d_position(lat2_start, lon2_start, alt2)
    P2_end = get_3d_position(lat2_end, lon2_end, alt2)
    
    # Calculate velocity vectors (position change per second)
    dt1 = t1_end - t1_start
    dt2 = t2_end - t2_start
    
    if dt1 > 0:
        V1 = (P1_end - P1_start) / dt1
    else:
        V1 = np.zeros(3)
    
    if dt2 > 0:
        V2 = (P2_end - P2_start) / dt2
    else:
        V2 = np.zeros(3)
    
    # Relative velocity
    V_rel = V1 - V2
    
    # At overlap_start, calculate initial positions
    if dt1 > 0:
        P1_at_overlap = P1_start + V1 * (overlap_start - t1_start)
    else:
        P1_at_overlap = P1_start
    
    if dt2 > 0:
        P2_at_overlap = P2_start + V2 * (overlap_start - t2_start)
    else:
        P2_at_overlap = P2_start
    
    # Initial separation at overlap_start
    P_rel_0 = P1_at_overlap - P2_at_overlap
    
    # Distance squared as function of time: D²(t) = ||P_rel_0 + V_rel * t||²
    # where t is time since overlap_start
    # D²(t) = ||P_rel_0||² + 2*P_rel_0·V_rel*t + ||V_rel||²*t²
    
    # To minimize, take derivative:
    # d/dt[D²(t)] = 2*P_rel_0·V_rel + 2*||V_rel||²*t = 0
    # Solve for t: t = -(P_rel_0·V_rel) / ||V_rel||²
    
    V_rel_squared = np.dot(V_rel, V_rel)
    
    if V_rel_squared < 1e-10:  # Aircraft moving in parallel at same speed
        # Distance is constant, use start of overlap
        t_cpa = overlap_start
        P1_cpa = P1_at_overlap
        P2_cpa = P2_at_overlap
    else:
        # Calculate time of CPA relative to overlap_start
        t_rel = -np.dot(P_rel_0, V_rel) / V_rel_squared
        
        # Convert to absolute time
        t_cpa_candidate = overlap_start + t_rel
        
        # Clamp to overlap window
        t_cpa = np.clip(t_cpa_candidate, overlap_start, overlap_end)
        
        # Calculate positions at CPA
        t_since_overlap = t_cpa - overlap_start
        P1_cpa = P1_at_overlap + V1 * t_since_overlap
        P2_cpa = P2_at_overlap + V2 * t_since_overlap
        
    # Distance squared as function of time: D²(t) = ||P_rel_0 + V_rel * t||²
    # D²(t) = a*t² + b*t + c
    a = np.dot(V_rel, V_rel)
    b = 2 * np.dot(P_rel_0, V_rel)
    c = np.dot(P_rel_0, P_rel_0) - horizontal_threshold_nm**2

        
    # Solve a*t² + b*t + c = 0 for t (relative to overlap_start)
    interval_start, interval_end = None, None
    if a != 0:
        discriminant = b**2 - 4*a*c
        if discriminant >= 0:
            sqrt_disc = np.sqrt(discriminant)
            t1 = (-b - sqrt_disc) / (2*a)
            t2 = (-b + sqrt_disc) / (2*a)
            # Sort and clamp to [0, overlap_end - overlap_start]
            t_low = max(0, min(t1, t2))
            t_high = min(overlap_end - overlap_start, max(t1, t2))
            if t_low <= t_high:
                interval_start = overlap_start + t_low
                interval_end = overlap_start + t_high
    elif b != 0:
        # Linear case
        t_cross = -c / b
        if 0 <= t_cross <= (overlap_end - overlap_start):
            interval_start = interval_end = overlap_start + t_cross
    else:
        # Constant distance, check if within threshold
        if c <= 0:
            interval_start = overlap_start
            interval_end = overlap_end
    
    # Calculate distance at CPA
    distance_vector = P1_cpa - P2_cpa
    
    # For horizontal distance, project onto horizontal plane
    # This is approximate but works well for collision detection
    distance_horizontal = np.sqrt(distance_vector[0]**2 + distance_vector[1]**2)
    
    return distance_horizontal, t_cpa, True, interval_start, interval_end


def detect_collisions(
    waypoints_df: pd.DataFrame,
    altitude_df: pd.DataFrame,
    horizontal_threshold_nm: float = 5.0,
    vertical_threshold_ft: float = 2000.0,
) -> pd.DataFrame:
    """
    Detect potential collisions using analytical CPA calculation.
    
    This is MUCH faster than sampling because it:
    1. Uses closed-form solution (no iteration)
    2. Gives exact CPA (not approximate)
    3. Vectorizable for batch processing
    
    Args:
        waypoints_df (pd.DataFrame): DataFrame from calculate_waypoint_times
        altitude_df (pd.DataFrame): DataFrame with altitude constraints per plane type
        coords_lookup (dict): Dictionary mapping waypoint codes to (lat, lon) tuples
        horizontal_threshold_nm (float): Horizontal separation threshold in nautical miles
        vertical_threshold_ft (float): Vertical separation threshold in feet
    
    Returns:
        pd.DataFrame: Collisions detected with CPA information
    """
    try:
        
        # Merge altitude information
        df = waypoints_df.merge(
            altitude_df[['Aircraft_Type', 'Min_altitude_ft', 'Max_altitude_ft', 'Optimal_altitude_min', 'Optimal_altitude_max']], 
            left_on='Plane_type', 
            right_on='Aircraft_Type', 
            how='left'
        )
        
        def parse_coord(coord):
            val = float(coord[:-1])
            return val if coord[-1] in 'NE' else -val

        from_lat = df['from'].str.split('/', expand=True)[0].apply(parse_coord)
        from_lon = df['from'].str.split('/', expand=True)[1].apply(parse_coord)
        to_lat = df['to'].str.split('/', expand=True)[0].apply(parse_coord)
        to_lon = df['to'].str.split('/', expand=True)[1].apply(parse_coord)

        df['from_lat_rad'] = np.radians(from_lat)
        df['from_lon_rad'] = np.radians(from_lon)
        df['to_lat_rad'] = np.radians(to_lat)
        df['to_lon_rad'] = np.radians(to_lon)
        
        df = df.sort_values('estimated_departure_time').reset_index(drop=True)
        
        collisions = []
        
        # Pre-filter: only compare segments with time overlap
        for idx1, row1 in df.iterrows():
            # Quick filter 1: Different aircraft with time overlap
            time_mask = (
                (df.index > idx1) &  # Only compare forward to avoid duplicates
                (df['ACID'] != row1['ACID']) &
                (df['estimated_departure_time'] <= row1['estimated_arrival_time']) &
                (df['estimated_arrival_time'] >= row1['estimated_departure_time'])
            )
            
            potential_conflicts = df[time_mask]
            
            if len(potential_conflicts) == 0:
                print(f"No potential conflicts for flight {row1['ACID']}.")
                continue
            
            # Quick filter 2: Check if chosen_altitude_ft ranges overlap within vertical threshold
            altitude_overlap_mask = (
                (potential_conflicts['chosen_altitude_ft'] - row1['chosen_altitude_ft'] <= vertical_threshold_ft) |
                (row1['chosen_altitude_ft'] - potential_conflicts['chosen_altitude_ft'] <= vertical_threshold_ft)
            )
            
            
            vertical_conflicts = potential_conflicts[altitude_overlap_mask]
            
            if len(vertical_conflicts) == 0:
                continue
            
            # Calculate CPA for each potential conflict
            for idx2, row2 in vertical_conflicts.iterrows():
                # Analytical CPA calculation
                cpa_dist, cpa_time, is_valid, interval_start, interval_end = calculate_cpa_analytical(
                    row1, row2, horizontal_threshold_nm
                )
                
                if not is_valid:
                    continue
                                
                # Check if CPA distance violates threshold
                if cpa_dist <= horizontal_threshold_nm:
                    # Calculate vertical separation
                    min_vertical_sep = max(
                        abs(row1['chosen_altitude_ft'] - row2['chosen_altitude_ft']),
                        abs(row2['chosen_altitude_ft'] - row1['chosen_altitude_ft']),
                    )
                                        
                    # Only add if both horizontal AND vertical thresholds violated
                    if min_vertical_sep <= vertical_threshold_ft:
                        overlap_start = max(row1['estimated_departure_time'], 
                                          row2['estimated_departure_time'])
                        overlap_end = min(row1['estimated_arrival_time'], 
                                        row2['estimated_arrival_time'])
                        
                        collisions.append({
                            'ACID_1': row1['ACID'],
                            'ACID_2': row2['ACID'],
                            'segment_1': row1['segment_number'],
                            'segment_2': row2['segment_number'],
                            'from_1': row1['from'],
                            'to_1': row1['to'],
                            'from_2': row2['from'],
                            'to_2': row2['to'],
                            'time_overlap_start': overlap_start,
                            'time_overlap_end': overlap_end,
                            'distance_threshold_cross_time_start': pd.Timestamp.fromtimestamp(interval_start) if interval_start else None,
                            'distance_threshold_cross_time_end': pd.Timestamp.fromtimestamp(interval_end) if interval_end else None,
                            'cpa_time': pd.Timestamp.fromtimestamp(cpa_time),
                            'cpa_distance_nm': round(cpa_dist, 3),
                            'min_vertical_separation_ft': round(min_vertical_sep, 0),
                            'altitude_1_min': row1['Min_altitude_ft'],
                            'altitude_1_max': row1['Max_altitude_ft'],
                            'altitude_2_min': row2['Min_altitude_ft'],
                            'altitude_2_max': row2['Max_altitude_ft'],
                            'severity': 'CRITICAL' if cpa_dist < 1.0 and min_vertical_sep < 500 else 'WARNING'
                        })
        
        collisions_df = pd.DataFrame(collisions)
        
        if len(collisions_df) > 0:
            collisions_df = collisions_df.sort_values('cpa_distance_nm').reset_index(drop=True)
        
        return collisions_df
        
    except Exception as e:
        print(f"An error occurred while detecting collisions: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

def get_ecef_from_coord(coord_str, altitude_ft):
    """
    Convert a coordinate string (e.g., '45.0N/75.0W') and altitude to ECEF.
    """
    lat_str, lon_str = coord_str.split('/')
    def parse_coord(val):
        v = float(val[:-1])
        return v if val[-1] in 'NE' else -v
    lat = np.radians(parse_coord(lat_str))
    lon = np.radians(parse_coord(lon_str))
    return get_3d_position(lat, lon, altitude_ft)

data_file = 'canadian_flights_1000.json'
df = load_data(data_file)

df = map_to_standard_formats(df)
waypoints_df = create_flight_waypoints(df)
lookup_df = create_flight_lookup(df)

altitude_df, speed_df = create_flight_constraints(lookup_df)
waypoints_df = calculate_travel_distances(waypoints_df)

flight_durations = calculate_flight_duration(waypoints_df, lookup_df, speed_df)
flight_durations = calculate_altitude(flight_durations, lookup_df, altitude_df)
flight_arrival_times = calculate_waypoint_times(flight_durations, lookup_df)

# --- Compose the final DataFrame with requested columns ---

# Merge in all required airplane/altitude/speed info
final_df = flight_arrival_times.merge(
    altitude_df[['Aircraft_Type', 'Optimal_altitude_min', 'Optimal_altitude_max']],
    left_on='Plane_type', right_on='Aircraft_Type', how='left'
).merge(
    speed_df[['Aircraft_Type', 'Max_cruise_Speed_knots', 'Min_cruise_Speed_knots', 'Min_Speed_knots', 'Max_Speed_knots']],
    left_on='Plane_type', right_on='Aircraft_Type', how='left',
    suffixes=('', '_speed')
)

# Compute from_ECEF and to_ECEF using chosen_altitude_ft for each segment
final_df['from_ECEF'] = final_df.apply(lambda row: get_ecef_from_coord(row['from'], row['chosen_altitude_ft']), axis=1)
final_df['to_ECEF'] = final_df.apply(lambda row: get_ecef_from_coord(row['to'], row['chosen_altitude_ft']), axis=1)

# Select and order the requested columns
flight_arrival_times = final_df[
    [
        'segment_number',
        'ACID',
        'from_ECEF',
        'to_ECEF',
        'travel_distance_nm',
        'Min_altitude_ft',
        'Max_altitude_ft',
        'Optimal_altitude_min',
        'Optimal_altitude_max',
        'Max_cruise_Speed_knots',
        'Min_cruise_Speed_knots',
        'Min_Speed_knots',
        'Max_Speed_knots',
        'estimated_departure_time',
        'estimated_arrival_time',
        'chosen_altitude_ft'
    ]
]