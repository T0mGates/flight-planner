# backend/scheduler/models.py
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
import numpy as np
import pandas as pd
from datetime import datetime
import os

from backend.scheduler.constants import TRANSLATION

REVERSE_TRANSLATION = {v: k for k, v in TRANSLATION.items()}

@dataclass
class FlightSegment:
    """Represents one waypoint-to-waypoint segment of a flight"""
    segment_number: int
    from_waypoint: str
    to_waypoint: str
    
    # Spatial
    from_ecef: np.ndarray
    to_ecef: np.ndarray
    travel_distance_nm: float
    
    # Altitude constraints
    min_altitude_ft: float
    max_altitude_ft: float
    optimal_altitude_min: float
    optimal_altitude_max: float
    chosen_altitude_ft: float
    
    # Speed constraints
    min_speed_knots: float
    max_speed_knots: float
    min_cruise_speed_knots: float
    max_cruise_speed_knots: float
    
    # Temporal
    estimated_departure_time: datetime
    estimated_arrival_time: datetime
    duration_sec: float
    
    @property
    def current_speed_knots(self) -> float:
        """Calculate current speed based on distance and duration"""
        return self.travel_distance_nm / (self.duration_sec / 3600)
    
    def to_optimizer_dict(self) -> dict:
        """Convert to format used by GeometryEngine"""
        return {
            'p1': self.from_ecef,
            'p2': self.to_ecef,
            't_start_orig': self.estimated_departure_time.timestamp(),
            'duration': self.duration_sec,
            'alt_orig': self.min_altitude_ft,
            'opt_min': self.optimal_altitude_min,
            'opt_max': self.optimal_altitude_max,
            'cruise_min': self.min_cruise_speed_knots,
            'cruise_max': self.max_cruise_speed_knots,
            'dist': self.travel_distance_nm
        }
    
    @staticmethod
    def from_dataframe_row(row: pd.Series) -> 'FlightSegment':
        """Create from DataFrame row"""
        return FlightSegment(
            segment_number=int(row['segment_number']),
            from_waypoint=str(row['from']),
            to_waypoint=str(row['to']),
            from_ecef=np.array(row['from_ECEF']),
            to_ecef=np.array(row['to_ECEF']),
            travel_distance_nm=float(row['travel_distance_nm']),
            min_altitude_ft=float(row['Min_altitude_ft']),
            max_altitude_ft=float(row['Max_altitude_ft']),
            optimal_altitude_min=float(row['Optimal_altitude_min']),
            optimal_altitude_max=float(row['Optimal_altitude_max']),
            chosen_altitude_ft=float(row['chosen_altitude_ft']),
            min_speed_knots=float(row['Min_Speed_knots']),
            max_speed_knots=float(row['Max_Speed_knots']),
            min_cruise_speed_knots=float(row['Min_cruise_Speed_knots']),
            max_cruise_speed_knots=float(row['Max_cruise_Speed_knots']),
            estimated_departure_time=pd.to_datetime(row['estimated_departure_time']),
            estimated_arrival_time=pd.to_datetime(row['estimated_arrival_time']),
            duration_sec=float((pd.to_datetime(row['estimated_arrival_time']) - 
                               pd.to_datetime(row['estimated_departure_time'])).total_seconds())
        )


@dataclass
class Flight:
    """Represents a complete flight with all segments"""
    acid: str
    plane_type: str
    departure_airport: str
    arrival_airport: str
    route: str
    passengers: int
    is_cargo: bool
    segments: List[FlightSegment] = field(default_factory=list)
    
    # Optimization state
    current_delay_sec: float = 0.0
    current_alt_shift_ft: float = 0.0
    
    # Metadata
    metadata: Dict = field(default_factory=dict)
    
    @property
    def departure_time(self) -> datetime:
        """Original scheduled departure time"""
        if self.segments:
            return self.segments[0].estimated_departure_time
        return datetime.now()
    
    @property
    def arrival_time(self) -> datetime:
        """Final arrival time"""
        if self.segments:
            return self.segments[-1].estimated_arrival_time
        return datetime.now()
    
    @property
    def total_distance_nm(self) -> float:
        """Total flight distance"""
        return sum(seg.travel_distance_nm for seg in self.segments)
    
    @property
    def total_duration_sec(self) -> float:
        """Total flight duration"""
        return sum(seg.duration_sec for seg in self.segments)
    
    def airports_as_names(self) -> Tuple[str, str]:
        """Return departure and arrival airport codes"""
        return (REVERSE_TRANSLATION.get(self.departure_airport), 
                REVERSE_TRANSLATION.get(self.arrival_airport))
    
    def get_position_at_time(self, timestamp: datetime) -> Optional[Tuple[np.ndarray, float]]:
        """
        Get ECEF position and altitude at a specific time.
        Returns (position, altitude) or None if time is outside flight window.
        """
        for seg in self.segments:
            if seg.estimated_departure_time <= timestamp <= seg.estimated_arrival_time:
                # Calculate fraction of segment completed
                elapsed = (timestamp - seg.estimated_departure_time).total_seconds()
                fraction = elapsed / seg.duration_sec
                
                # Linear interpolation
                position = seg.from_ecef + fraction * (seg.to_ecef - seg.from_ecef)
                return position, seg.chosen_altitude_ft
        
        return None
    
    def to_optimizer_dict(self) -> dict:
        """Convert to format used by CostDriven4DResolver"""
        return {
            'acid': self.acid,
            'segments': [seg.to_optimizer_dict() for seg in self.segments],
            'current_delay': self.current_delay_sec,
            'current_alt_shift': self.current_alt_shift_ft,
            'pax': self.passengers
        }
        
    def to_api_dict(self, flight_id: int) -> dict:
        """Convert to FastAPI output format (JSON-serializable)"""
        return {
            "departure_airport": str(self.departure_airport),
            "arrival_airport": str(self.arrival_airport),
            "route": str(self.route),
            "ACID": str(self.acid),
            "plane_type": str(self.plane_type),
            "is_cargo": bool(self.is_cargo),
            "aircraft_speed": [float(seg.current_speed_knots) for seg in self.segments],
            "departure_time": int(self.departure_time.timestamp()),
            "altitude": [float(seg.chosen_altitude_ft) for seg in self.segments],
            "passengers": int(self.passengers),
            "id": int(flight_id)
        }
    
    def apply_optimization(self, alt_shift_ft: float, delay_sec: float):
        """Apply optimization results to all segments"""
        self.current_alt_shift_ft = alt_shift_ft
        self.current_delay_sec = delay_sec
        
        delay_td = pd.Timedelta(seconds=delay_sec)
        for seg in self.segments:
            seg.chosen_altitude_ft += alt_shift_ft
            seg.estimated_departure_time += delay_td
            seg.estimated_arrival_time += delay_td
    
    @staticmethod
    def from_dataframe_group(acid: str, group_df: pd.DataFrame) -> 'Flight':
        """Create Flight from grouped DataFrame"""
        group_df = group_df.sort_values('segment_number')
        first_row = group_df.iloc[0]
        last_row = group_df.iloc[-1]
        
        segments = [FlightSegment.from_dataframe_row(row) for _, row in group_df.iterrows()]
        
        return Flight(
            acid=acid,
            plane_type=str(first_row.get('Plane_type', '')),
            departure_airport=str(first_row.get('from', '')),
            arrival_airport=str(last_row.get('to', '')),
            route=str(first_row.get('route', '')),
            passengers=int(first_row.get('passengers', 0)),
            is_cargo=bool(first_row.get('is_cargo', False)),
            segments=segments
        )


class FlightSchedule:
    """
    Container for managing multiple flights with collision detection,
    conversion utilities, and scheduling operations.
    """
    
    def __init__(self, flights: List[Flight] = None):
        self.flights = flights or []
        self._collision_cache = {}
        self._cache_valid = False
    
    def __len__(self) -> int:
        return len(self.flights)
    
    def __iter__(self):
        return iter(self.flights)
    
    def __getitem__(self, index):
        return self.flights[index]
    
    # ===== FACTORY METHODS =====
    
    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> 'FlightSchedule':
        """Create FlightSchedule from scheduler DataFrame"""
        flights = []
        for acid, group in df.groupby('ACID'):
            flights.append(Flight.from_dataframe_group(acid, group))
        return cls(flights)
    
    @classmethod
    def from_json_file(cls, file_path: str) -> 'FlightSchedule':
        """
        Load flight schedule directly from JSON file.
        Full pipeline from raw JSON to structured FlightSchedule.
        """
        from backend.scheduler.constants import EARTH_RADIUS_NM, FEET_TO_NM, TRANSLATION, PLANE_TYPE_MAP
        from backend.scheduler.helpers import haversine_vectorized
        from backend.scheduler.lookups import create_flight_constraints
        
        # Helper function for ECEF conversion
        def get_ecef_from_coord(coord_str: str, altitude_ft: float) -> np.ndarray:
            lat_str, lon_str = coord_str.split('/')
            
            def parse_coord(val: str) -> float:
                v = float(val[:-1])
                return v if val[-1] in 'NE' else -v
            
            lat = np.radians(parse_coord(lat_str))
            lon = np.radians(parse_coord(lon_str))
            
            R = EARTH_RADIUS_NM + (altitude_ft * FEET_TO_NM)
            
            return np.array([
                R * np.cos(lat) * np.cos(lon),
                R * np.cos(lat) * np.sin(lon),
                R * np.sin(lat)
            ])
        
        # 1. Load raw data
        base_dir = os.path.dirname(os.path.abspath(__file__))
        abs_path = os.path.join(base_dir, file_path)
        df = pd.read_json(abs_path)
        df.columns = [col.replace(' ', '_') for col in df.columns]
        
        # 2. Translate airport codes and plane types
        df['arrival_airport'] = df['arrival_airport'].map(TRANSLATION)
        df['departure_airport'] = df['departure_airport'].map(TRANSLATION)
        df['Plane_type'] = df['Plane_type'].map(PLANE_TYPE_MAP)
        
        # 3. Flatten routes into waypoint segments
        waypoints_list = []
        for _, row in df.iterrows():
            route_points = [row['departure_airport']] + row['route'].split() + [row['arrival_airport']]
            
            for i in range(len(route_points) - 1):
                waypoints_list.append({
                    'route': row['route'],
                    'segment_number': i + 1,
                    'ACID': row['ACID'],
                    'Plane_type': row['Plane_type'],
                    'from': route_points[i],
                    'to': route_points[i + 1],
                    'passengers': row.get('passengers', 200),
                    'is_cargo': row.get('is_cargo', False),
                    'departure_time_orig': row['departure_time']
                })
        
        wp_df = pd.DataFrame(waypoints_list)
        
        # 4. Integrate aircraft constraints
        alt_constraints, speed_constraints = create_flight_constraints()
        
        wp_df = wp_df.merge(
            alt_constraints, 
            left_on='Plane_type', 
            right_on='Aircraft_Type', 
            how='left'
        )
        wp_df = wp_df.merge(
            speed_constraints, 
            left_on='Plane_type', 
            right_on='Aircraft_Type', 
            how='left', 
            suffixes=('', '_s')
        )
        
        # 5. Calculate physics
        wp_df['travel_distance_nm'] = haversine_vectorized(wp_df)
        wp_df['duration_sec'] = (wp_df['travel_distance_nm'] / wp_df['Max_cruise_Speed_knots']) * 3600
        wp_df['chosen_altitude_ft'] = wp_df['Min_altitude_ft']
        
        # 6. Calculate temporal windows
        wp_df['departure_time_dt'] = pd.to_datetime(wp_df['departure_time_orig'], unit='s')
        wp_df = wp_df.sort_values(['ACID', 'segment_number'])
        
        wp_df['cum_duration'] = wp_df.groupby('ACID')['duration_sec'].cumsum()
        wp_df['estimated_arrival_time'] = (
            wp_df['departure_time_dt'] + pd.to_timedelta(wp_df['cum_duration'], unit='s')
        )
        wp_df['estimated_departure_time'] = (
            wp_df['estimated_arrival_time'] - pd.to_timedelta(wp_df['duration_sec'], unit='s')
        )
        
        # 7. Spatial conversion (ECEF)
        wp_df['from_ECEF'] = wp_df.apply(
            lambda r: get_ecef_from_coord(r['from'], r['chosen_altitude_ft']), 
            axis=1
        )
        wp_df['to_ECEF'] = wp_df.apply(
            lambda r: get_ecef_from_coord(r['to'], r['chosen_altitude_ft']), 
            axis=1
        )
        
        # 8. Return as FlightSchedule
        return cls.from_dataframe(wp_df.sort_values('estimated_departure_time'))
    
    @classmethod
    def from_compact_dataframe(cls, df: pd.DataFrame) -> 'FlightSchedule':
        """
        Load flight schedule from compact DataFrame format.
        
        Each row represents one complete flight (not segments).
        
        Expected columns:
            - departure_airport: str (e.g., "CYVR")
            - arrival_airport: str (e.g., "CYYC")
            - route: str (e.g., "50.77N/115.66W 51.0N/114.0W")
            - ACID: str (e.g., "ACA821")
            - plane_type: str (e.g., "Boeing 787-9")
            - is_cargo: bool
            - aircraft_speed: float or list of floats
            - departure_time: int (unix timestamp)
            - altitude: float or list of floats
            - passengers: int
            - id: int (optional)
        
        Args:
            df: DataFrame with one row per flight
            
        Returns:
            FlightSchedule with loaded flights
        """
        # Convert DataFrame to API dict format
        api_data = {}
        
        for idx, row in df.iterrows():
            flight_id = str(row.get('id', idx + 1))
            
            api_data[flight_id] = {
                'departure_airport': str(row['departure_airport']),
                'arrival_airport': str(row['arrival_airport']),
                'route': str(row['route']),
                'ACID': str(row['ACID']),
                'plane_type': str(row['plane_type']),
                'is_cargo': bool(row.get('is_cargo', False)),
                'aircraft_speed': row['aircraft_speed'],
                'departure_time': int(row['departure_time']),
                'altitude': row['altitude'],
                'passengers': int(row.get('passengers', 0)),
                'id': int(row.get('id', idx + 1))
            }
        
        # Use existing from_api_dict method
        return cls.from_api_dict(api_data)
    
    @classmethod
    def from_api_dict(cls, api_data: dict) -> 'FlightSchedule':
        """
        Load flight schedule from API dictionary format.
        
        Expected format:
        {
            "1": {
                "departure_airport": "CYVR",
                "arrival_airport": "CYYC",
                "route": "50.77N/115.66W",
                "ACID": "ACA821",
                "plane_type": "Boeing 787-9",
                "is_cargo": false,
                "aircraft_speed": [500.0, 510.0] or 500.0,
                "departure_time": 1767780000,
                "altitude": [28000, 29000] or 28000,
                "passengers": 229,
                "id": 1
            },
            ...
        }
        
        Args:
            api_data: Dictionary with string keys and flight dictionaries
            
        Returns:
            FlightSchedule with loaded flights
        """
        from backend.scheduler.constants import EARTH_RADIUS_NM, FEET_TO_NM
        from backend.scheduler.helpers import haversine_vectorized
        from backend.scheduler.lookups import create_flight_constraints
        
        # Helper function for ECEF conversion
        def get_ecef_from_coord(coord_str: str, altitude_ft: float) -> np.ndarray:
            lat_str, lon_str = coord_str.split('/')
            
            def parse_coord(val: str) -> float:
                v = float(val[:-1])
                return v if val[-1] in 'NE' else -v
            
            lat = np.radians(parse_coord(lat_str))
            lon = np.radians(parse_coord(lon_str))
            
            R = EARTH_RADIUS_NM + (altitude_ft * FEET_TO_NM)
            
            return np.array([
                R * np.cos(lat) * np.cos(lon),
                R * np.cos(lat) * np.sin(lon),
                R * np.sin(lat)
            ])
        
        # Get aircraft constraints
        alt_constraints, speed_constraints = create_flight_constraints()
        
        # Convert to dict keyed by aircraft type for fast lookup
        alt_lookup = alt_constraints.set_index('Aircraft_Type').to_dict('index')
        speed_lookup = speed_constraints.set_index('Aircraft_Type').to_dict('index')
        
        flights = []
        
        for flight_id, flight_data in api_data.items():
            acid = flight_data['ACID']
            plane_type = flight_data['plane_type']
            route_str = flight_data['route']
            dep_airport = flight_data['departure_airport']
            arr_airport = flight_data['arrival_airport']
            
            # Handle both single values and lists for altitude/speed
            altitudes = flight_data['altitude']
            if not isinstance(altitudes, list):
                altitudes = [altitudes]
            
            speeds = flight_data['aircraft_speed']
            if not isinstance(speeds, list):
                speeds = [speeds]
            
            # Parse route: departure -> waypoints -> arrival
            waypoints = route_str.split() if route_str else []
            route_points = [dep_airport] + waypoints + [arr_airport]
            
            # Get aircraft constraints
            alt_cons = alt_lookup.get(plane_type, {})
            speed_cons = speed_lookup.get(plane_type, {})
            
            # Create segments
            segments = []
            departure_time = pd.to_datetime(flight_data['departure_time'], unit='s')
            current_time = departure_time
            
            for seg_num in range(len(route_points) - 1):
                from_wp = route_points[seg_num]
                to_wp = route_points[seg_num + 1]
                
                # Use segment-specific altitude/speed if available, otherwise use first
                altitude = altitudes[seg_num] if seg_num < len(altitudes) else altitudes[0]
                speed = speeds[seg_num] if seg_num < len(speeds) else speeds[0]
                
                # Calculate distance using haversine (simplified version)
                # Create temp dataframe for haversine function
                temp_df = pd.DataFrame([{
                    'from': from_wp,
                    'to': to_wp
                }])
                distance_nm = haversine_vectorized(temp_df)[0]
                
                # Calculate duration based on speed
                duration_sec = (distance_nm / speed) * 3600
                
                # Create ECEF coordinates
                from_ecef = get_ecef_from_coord(from_wp, altitude)
                to_ecef = get_ecef_from_coord(to_wp, altitude)
                
                # Create segment
                segment = FlightSegment(
                    segment_number=seg_num + 1,
                    from_waypoint=from_wp,
                    to_waypoint=to_wp,
                    from_ecef=from_ecef,
                    to_ecef=to_ecef,
                    travel_distance_nm=distance_nm,
                    min_altitude_ft=alt_cons.get('Min_altitude_ft', altitude),
                    max_altitude_ft=alt_cons.get('Max_altitude_ft', altitude + 10000),
                    optimal_altitude_min=alt_cons.get('Optimal_altitude_min', altitude),
                    optimal_altitude_max=alt_cons.get('Optimal_altitude_max', altitude + 2000),
                    chosen_altitude_ft=altitude,
                    min_speed_knots=speed_cons.get('Min_Speed_knots', speed * 0.8),
                    max_speed_knots=speed_cons.get('Max_Speed_knots', speed * 1.2),
                    min_cruise_speed_knots=speed_cons.get('Min_cruise_Speed_knots', speed * 0.9),
                    max_cruise_speed_knots=speed_cons.get('Max_cruise_Speed_knots', speed * 1.1),
                    estimated_departure_time=current_time,
                    estimated_arrival_time=current_time + pd.Timedelta(seconds=duration_sec),
                    duration_sec=duration_sec
                )
                
                segments.append(segment)
                current_time = segment.estimated_arrival_time
            
            # Create flight
            flight = Flight(
                acid=acid,
                plane_type=plane_type,
                departure_airport=dep_airport,
                arrival_airport=arr_airport,
                route=route_str,
                passengers=flight_data.get('passengers', 0),
                is_cargo=flight_data.get('is_cargo', False),
                segments=segments
            )
            
            flights.append(flight)
        
        return cls(flights)
    
    # ===== CONVERSION METHODS =====
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert back to DataFrame format"""
        rows = []
        for flight in self.flights:
            for seg in flight.segments:
                rows.append({
                    'segment_number': seg.segment_number,
                    'ACID': flight.acid,
                    'from': seg.from_waypoint,
                    'to': seg.to_waypoint,
                    'from_ECEF': seg.from_ecef,
                    'to_ECEF': seg.to_ecef,
                    'travel_distance_nm': seg.travel_distance_nm,
                    'Min_altitude_ft': seg.min_altitude_ft,
                    'Max_altitude_ft': seg.max_altitude_ft,
                    'Optimal_altitude_min': seg.optimal_altitude_min,
                    'Optimal_altitude_max': seg.optimal_altitude_max,
                    'chosen_altitude_ft': seg.chosen_altitude_ft,
                    'Min_Speed_knots': seg.min_speed_knots,
                    'Max_Speed_knots': seg.max_speed_knots,
                    'Min_cruise_Speed_knots': seg.min_cruise_speed_knots,
                    'Max_cruise_Speed_knots': seg.max_cruise_speed_knots,
                    'estimated_departure_time': seg.estimated_departure_time,
                    'estimated_arrival_time': seg.estimated_arrival_time,
                    'passengers': flight.passengers,
                    'is_cargo': flight.is_cargo,
                    'route': flight.route,
                    'Plane_type': flight.plane_type
                })
        return pd.DataFrame(rows)
    
    def to_optimizer_dict(self) -> dict:
        """Convert to optimizer's internal format"""
        return {flight.acid: flight.to_optimizer_dict() for flight in self.flights}
    
    def to_api_dict(self) -> dict:
        """Convert to FastAPI output format"""
        return {
            flight.acid: flight.to_api_dict(i + 1) 
            for i, flight in enumerate(self.flights)
        }
        
    def to_database_flight(self) -> List[Flight]:
        """Convert to list of Flight models for database insertion"""
        from backend.models import Flight as DBFlight
        db_flights = []
        for flight in self.flights:
            dep, arr = flight.airports_as_names()
            db_flight = DBFlight(
                departure_airport=dep,
                arrival_airport=arr,
                route=flight.route,
                ACID=flight.acid,
                plane_type=flight.plane_type,
                is_cargo=flight.is_cargo,
                aircraft_speed=[seg.current_speed_knots for seg in flight.segments],
                departure_time=int(flight.departure_time.timestamp()),
                altitude=[seg.chosen_altitude_ft for seg in flight.segments],
                passengers=flight.passengers
            )
            db_flights.append(db_flight)
        return db_flights
    
    # ===== COLLISION DETECTION =====
    
    def calculate_segment_cpa(self, seg1: FlightSegment, seg2: FlightSegment, 
                              min_separation_nm: float = 5.0) -> float:
        """
        Calculate Closest Point of Approach (CPA) between two flight segments.
        Returns distance in nautical miles.
        """
        # 1. Vertical separation check
        if abs(seg1.chosen_altitude_ft - seg2.chosen_altitude_ft) >= 2000:
            return 999.0
        
        # 2. Time window overlap
        ts1 = seg1.estimated_departure_time.timestamp()
        te1 = seg1.estimated_arrival_time.timestamp()
        ts2 = seg2.estimated_departure_time.timestamp()
        te2 = seg2.estimated_arrival_time.timestamp()
        
        t_overlap = [max(ts1, ts2), min(te1, te2)]
        
        if t_overlap[0] >= t_overlap[1]:
            return 999.0  # No temporal overlap
        
        # 3. Vector calculation
        v1 = (seg1.to_ecef - seg1.from_ecef) / seg1.duration_sec
        v2 = (seg2.to_ecef - seg2.from_ecef) / seg2.duration_sec
        
        p1_at_start = seg1.from_ecef + v1 * (t_overlap[0] - ts1)
        p2_at_start = seg2.from_ecef + v2 * (t_overlap[0] - ts2)
        
        dp = p1_at_start - p2_at_start
        dv = v1 - v2
        
        # 4. Minimize distance
        dv2 = np.dot(dv, dv)
        if dv2 > 1e-9:
            t_cpa = np.clip(-np.dot(dp, dv)/dv2, 0, t_overlap[1] - t_overlap[0])
        else:
            t_cpa = 0
        
        return np.linalg.norm(dp + dv * t_cpa)
    
    def check_flight_collision(self, flight1: Flight, flight2: Flight, 
                               min_separation_nm: float = 5.0) -> bool:
        """Check if two flights have any colliding segments"""
        for seg1 in flight1.segments:
            for seg2 in flight2.segments:
                cpa = self.calculate_segment_cpa(seg1, seg2, min_separation_nm)
                if cpa < min_separation_nm:
                    return True
        return False
    
    def count_collisions(self, min_separation_nm: float = 5.0, 
                        time_window_hours: float = 2.0) -> int:
        """
        Count total number of collision pairs in the schedule.
        Only checks flights within time_window_hours of each other for efficiency.
        """
        collision_count = 0
        time_window_sec = time_window_hours * 3600
        
        for i in range(len(self.flights)):
            for j in range(i + 1, len(self.flights)):
                f1, f2 = self.flights[i], self.flights[j]
                
                # Temporal filter
                time_diff = abs((f1.departure_time - f2.departure_time).total_seconds())
                if time_diff > time_window_sec:
                    continue
                
                if self.check_flight_collision(f1, f2, min_separation_nm):
                    collision_count += 1
        
        return collision_count
    
    def get_collision_pairs(self, min_separation_nm: float = 5.0,
                           time_window_hours: float = 2.0) -> List[Tuple[str, str, float]]:
        """
        Get list of all colliding flight pairs with their minimum CPA.
        Returns list of (acid1, acid2, min_cpa_distance)
        """
        collisions = []
        time_window_sec = time_window_hours * 3600
        
        for i in range(len(self.flights)):
            for j in range(i + 1, len(self.flights)):
                f1, f2 = self.flights[i], self.flights[j]
                
                # Temporal filter
                time_diff = abs((f1.departure_time - f2.departure_time).total_seconds())
                if time_diff > time_window_sec:
                    continue
                
                # Find minimum CPA across all segment pairs
                min_cpa = float('inf')
                for seg1 in f1.segments:
                    for seg2 in f2.segments:
                        cpa = self.calculate_segment_cpa(seg1, seg2, min_separation_nm)
                        min_cpa = min(min_cpa, cpa)
                
                if min_cpa < min_separation_nm:
                    collisions.append((f1.acid, f2.acid, min_cpa))
        
        return collisions
    
    # ===== UTILITY METHODS =====
    
    def get_flight(self, acid: str) -> Optional[Flight]:
        """Get flight by ACID"""
        for flight in self.flights:
            if flight.acid == acid:
                return flight
        return None
    
    def add_flight(self, flight: Flight):
        """Add a flight to the schedule"""
        self.flights.append(flight)
        self._cache_valid = False
    
    def remove_flight(self, acid: str) -> bool:
        """Remove a flight by ACID. Returns True if found and removed."""
        for i, flight in enumerate(self.flights):
            if flight.acid == acid:
                del self.flights[i]
                self._cache_valid = False
                return True
        return False
    
    def sort_by_departure(self):
        """Sort flights by departure time"""
        self.flights.sort(key=lambda f: f.departure_time)
    
    def get_statistics(self) -> dict:
        """Get summary statistics about the schedule"""
        if not self.flights:
            return {}
        
        return {
            'total_flights': len(self.flights),
            'total_passengers': sum(f.passengers for f in self.flights),
            'cargo_flights': sum(1 for f in self.flights if f.is_cargo),
            'passenger_flights': sum(1 for f in self.flights if not f.is_cargo),
            'total_distance_nm': sum(f.total_distance_nm for f in self.flights),
            'earliest_departure': min(f.departure_time for f in self.flights),
            'latest_arrival': max(f.arrival_time for f in self.flights),
            'unique_aircraft_types': len(set(f.plane_type for f in self.flights)),
            'collisions': self.count_collisions()
        }