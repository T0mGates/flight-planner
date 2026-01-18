import numpy as np
import pandas as pd
from collections import defaultdict

from backend.scheduler.data_loader import generate_flight_schedule

# --- MODULE 1: GEOMETRY ENGINE ---
class GeometryEngine:
    """
    Pure mathematical module for 4D spatial calculations.
    Calculates CPA (Closest Point of Approach) between two flight segments.
    """
    @staticmethod
    def get_segment_cpa(s1, s2, d1, a1, d2, a2, min_sep):
        # 1. Vertical Check: If altitudes differ by >= 2000ft, they are safe.
        if abs((s1['alt_orig'] + a1) - (s2['alt_orig'] + a2)) >= 2000:
            return 999.0
            
        # 2. Time Window Check: Find the overlapping time interval.
        ts1, ts2 = s1['t_start_orig'] + d1, s2['t_start_orig'] + d2
        te1, te2 = ts1 + s1['duration'], ts2 + s2['duration']
        
        t_overlap = [max(ts1, ts2), min(te1, te2)]
        if t_overlap[0] >= t_overlap[1]: 
            return 999.0 # No temporal overlap
        
        # 3. Vector Calculation: Position p(t) = p_start + velocity * t
        v1 = (s1['p2'] - s1['p1']) / s1['duration']
        v2 = (s2['p2'] - s2['p1']) / s2['duration']
        
        # Relative position and velocity at the start of the overlap
        p1_at_start = s1['p1'] + v1 * (t_overlap[0] - ts1)
        p2_at_start = s2['p1'] + v2 * (t_overlap[0] - ts2)
        
        dp = p1_at_start - p2_at_start
        dv = v1 - v2
        
        # 4. Minimize Distance Squared: f(t) = |dp + dv*t|^2
        dv2 = np.dot(dv, dv)
        if dv2 > 1e-9:
            # Time of closest approach within the overlap window
            t_cpa = np.clip(-np.dot(dp, dv)/dv2, 0, t_overlap[1] - t_overlap[0])
        else:
            t_cpa = 0 # Parallel trajectories
            
        return np.linalg.norm(dp + dv * t_cpa)

# --- MODULE 2: COST ENGINE ---
class CostEngine:
    """
    Handles economic penalty logic. 
    Balance fuel efficiency (altitude/speed) against operational costs (delay).
    """
    @staticmethod
    def calculate_penalty(f, alt_shift, delay_sec):
        # Hard constraint: Flights cannot depart earlier than scheduled
        if delay_sec < 0: return 1e18 
        
        pax = f['pax']
        # Quadratic Delay Cost: Exponentially penalize long delays
        cost = ((delay_sec / 60.0)**2) * pax
        
        for s in f['segments']:
            curr_alt = s['alt_orig'] + alt_shift
            # Altitude deviation cost: $5 per foot outside optimal range
            if curr_alt < s['opt_min']: 
                cost += (s['opt_min'] - curr_alt) * 5
            elif curr_alt > s['opt_max']: 
                cost += (curr_alt - s['opt_max']) * 5
            
            # Speed deviation cost: Penalize if speed is pushed outside cruise limits
            speed = s['dist'] / (s['duration'] / 3600)
            if speed < s['cruise_min']: 
                cost += (s['cruise_min'] - speed) * pax
            elif speed > s['cruise_max']: 
                cost += (speed - s['cruise_max']) * pax
        return cost

# --- MODULE 3: DATA PREPROCESSOR ---
class FlightDataParser:
    """
    Converts raw DataFrames into optimized dictionaries for fast iteration.
    """
    @staticmethod
    def to_internal_format(df):
        flights = {}
        for acid, group in df.groupby('ACID'):
            group = group.sort_values('segment_number')
            # Extract list of segments with ECEF coordinates
            segments = [{
                'p1': np.array(r['from_ECEF']), 'p2': np.array(r['to_ECEF']),
                't_start_orig': r['estimated_departure_time'].timestamp(),
                'duration': (r['estimated_arrival_time'] - r['estimated_departure_time']).total_seconds(),
                'alt_orig': r['Min_altitude_ft'], 'opt_min': r['Optimal_altitude_min'],
                'opt_max': r['Optimal_altitude_max'], 'cruise_min': r['Min_cruise_Speed_knots'],
                'cruise_max': r['Max_cruise_Speed_knots'], 'dist': r['travel_distance_nm']
            } for _, r in group.iterrows()]
            
            flights[acid] = {
                'acid': acid, 'segments': segments, 'current_delay': 0.0, 
                'current_alt_shift': 0.0, 'pax': group.get('passengers', pd.Series([200]*len(group))).iloc[0]
            }
        return flights

# --- MODULE 4: CORE RESOLVER ---
class CostDriven4DResolver:
    def __init__(self, min_sep_nm=5.0):
        self.min_sep_nm = min_sep_nm
        self.conflict_cost = 1e13 # Penalty must be higher than any possible maneuver cost
        
        # Define search neighborhood
        self.maneuvers = [(0, 300), (0, 600), (2000, 0), (-2000, 0), (2000, 300), (-2000, 300)]
        self.larger_maneuvers = [(0, 1800), (0, 3600), (4000, 0), (6000, 0), (-4000, 0), (-6000, 0)]

    def resolve(self, df, iterations=30, status={}):
        
        status['Message'] = "Starting parsing..."
        status['Total Iterations'] = iterations
        status['Current Iteration'] = 0
        
        flights = FlightDataParser.to_internal_format(df)
        active_neighborhood = self.maneuvers.copy()
        
        status['Message'] = "Optimizing..."

        for it in range(iterations):           
            status['Current Iteration'] = it + 1
            # A. Update Temporal Neighbors (Broad Phase)
            # We look for ANY flight within 1 hour to prevent creating new collisions
            potential_nb = defaultdict(set)
            f_list = list(flights.values())
            collision_count = 0
            
            for i in range(len(f_list)):
                for j in range(i + 1, len(f_list)):
                    fa, fb = f_list[i], f_list[j]
                    # Temporal filter (7200s = 2 hours)
                    if abs(fa['segments'][0]['t_start_orig'] - fb['segments'][0]['t_start_orig']) > 7200: continue
                    
                    # Mark as neighbors to check during optimization
                    potential_nb[fa['acid']].add(fb['acid'])
                    potential_nb[fb['acid']].add(fa['acid'])

                    # Count active collisions for status reporting
                    if self._check_collision(fa, fb):
                        collision_count += 1

            # B. Optimization Step
            changes_made = 0
            # Shuffle or sort by cost to prevent deterministic "hovering" cycles
            order = sorted(flights.keys(), key=lambda x: CostEngine.calculate_penalty(flights[x], 0, 0), reverse=True)
            
            for acid in order:
                f = flights[acid]
                
                def get_total_local_cost(a_s, d_s):
                    # Economic cost + Collision penalties against all potential neighbors
                    score = CostEngine.calculate_penalty(f, a_s, d_s)
                    for nb_id in potential_nb[acid]:
                        nb = flights[nb_id]
                        if self._check_collision_custom(f, nb, a_s, d_s):
                            score += self.conflict_cost
                    return score

                best_score = get_total_local_cost(f['current_alt_shift'], f['current_delay'])
                best_move = (f['current_alt_shift'], f['current_delay'])

                # Search through maneuvers
                for m_a, m_d in active_neighborhood:
                    test_a, test_d = f['current_alt_shift'] + m_a, f['current_delay'] + m_d
                    current_move_score = get_total_local_cost(test_a, test_d)
                    
                    if current_move_score < best_score:
                        best_score = current_move_score
                        best_move = (test_a, test_d)
                
                if best_move != (f['current_alt_shift'], f['current_delay']):
                    f['current_alt_shift'], f['current_delay'] = best_move
                    changes_made += 1
                    
            print(f"Iteration {it+1:2d} | Active Conflicts: {collision_count:3d} | Changes: {changes_made:3d}")
            status['Active Conflicts'] = collision_count
            status['Total Conflicts'] = max(status.get('Total Conflicts', 0), collision_count)
            status['Optimization Changes'] = status.get('Optimization Changes', 0) + changes_made

            # C. Escape Local Minima Logic
            if changes_made == 0 and collision_count > 0:
                print(">> STUCK: Expanding maneuver search space...")
                active_neighborhood = list(set(self.maneuvers + self.larger_maneuvers))
            elif collision_count == 0:
                print(">> SUCCESS: All conflicts resolved.")
                break

        return self._finalize(df, flights)

    def _check_collision(self, f1, f2):
        """Checks if two flights collide at their current delay/altitude settings."""
        return self._check_collision_custom(f1, f2, f1['current_alt_shift'], f1['current_delay'])

    def _check_collision_custom(self, f1, f2, alt1, del1):
        """Flexible collision check for hypothetical moves."""
        for s1 in f1['segments']:
            for s2 in f2['segments']:
                d = GeometryEngine.get_segment_cpa(s1, s2, del1, alt1, f2['current_delay'], f2['current_alt_shift'], self.min_sep_nm)
                if d < self.min_sep_nm: return True
        return False

    def _finalize(self, df, flights):
        out = df.copy()
        for acid, f in flights.items():
            mask = out['ACID'] == acid
            out.loc[mask, 'chosen_altitude_ft'] += f['current_alt_shift']
            dt = pd.Timedelta(seconds=f['current_delay'])
            out.loc[mask, 'estimated_departure_time'] += dt
            out.loc[mask, 'estimated_arrival_time'] += dt        

        out['knots'] = out['travel_distance_nm'] / ((out['estimated_arrival_time'] - out['estimated_departure_time']).dt.total_seconds() / 3600)
        out.drop(columns=['from_ECEF', 'to_ECEF', 'Min_altitude_ft', 'Max_altitude_ft',
                          'Optimal_altitude_min', 'Optimal_altitude_max',
                          'Min_cruise_Speed_knots', 'Max_cruise_Speed_knots',
                          'travel_distance_nm', 'Min_Speed_knots', 'Max_Speed_knots'], inplace=True)
 
        return out
    
    @staticmethod
    def format_for_fastapi(df):
        # altitudes and speed should be list of floats, sorted by segment_number
        # this will return df in following format:
        identifier = 1
        output = {}
        
        df.sort_values(['ACID', 'segment_number'], inplace=True)
        
        # group by ACID and then create entries
        for _, group in df.groupby('ACID'):
            group = group.sort_values('segment_number')
            altitudes = group['chosen_altitude_ft'].tolist()
            speeds = group['knots'].tolist()
            output[str(identifier)] = {
                "departure_airport": str(group['from_airport'].iloc[0]) if 'from_airport' in group else str(group['from'].iloc[0]),
                "arrival_airport": str(group['to_airport'].iloc[0]) if 'to_airport' in group else str(group['to'].iloc[0]),
                "route": str(group['route'].iloc[0]) if 'route' in group else "",
                "ACID": str(group['ACID'].iloc[0]),
                "plane_type": str(group['Plane_type'].iloc[0]) if 'Plane_type' in group else "",
                "is_cargo": bool(group['is_cargo'].iloc[0]) if 'is_cargo' in group else False,
                "aircraft_speed": [float(s) for s in speeds],
                "departure_time": int(group['estimated_departure_time'].iloc[0].timestamp()),
                "altitude": [float(a) for a in altitudes],
                "passengers": int(group['passengers'].iloc[0]) if 'passengers' in group else 0,
                "id": int(identifier)
            }
            
            identifier += 1
            
        print(output)
                
        return output
        
            
            
if __name__ == "__main__":    
    # Load flight schedule
    flight_arrival_times = generate_flight_schedule('canadian_flights_1000.json')

    # Initialize resolver
    resolver = CostDriven4DResolver(min_sep_nm=5.0)

    # Resolve conflicts
    resolved_df = resolver.resolve(flight_arrival_times, iterations=2)

    # Display results
    print(resolved_df)