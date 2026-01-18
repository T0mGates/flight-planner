# backend/scheduler/resolver.py
import numpy as np
from collections import defaultdict
from backend.scheduler.models import FlightSchedule


# --- MODULE 1: GEOMETRY ENGINE ---
class GeometryEngine:
    """Pure mathematical module for 4D spatial calculations."""
    
    @staticmethod
    def get_segment_cpa(s1, s2, d1, a1, d2, a2, min_sep):
        """
        Calculate Closest Point of Approach between two flight segments.
        
        Args:
            s1, s2: Segment dictionaries from to_optimizer_dict()
            d1, d2: Delay adjustments in seconds
            a1, a2: Altitude adjustments in feet
            min_sep: Minimum separation in nautical miles
            
        Returns:
            Distance at closest approach in nautical miles
        """
        # 1. Vertical separation check
        if abs((s1['alt_orig'] + a1) - (s2['alt_orig'] + a2)) >= 2000:
            return 999.0
        
        # 2. Time window overlap
        ts1, ts2 = s1['t_start_orig'] + d1, s2['t_start_orig'] + d2
        te1, te2 = ts1 + s1['duration'], ts2 + s2['duration']
        t_overlap = [max(ts1, ts2), min(te1, te2)]
        
        if t_overlap[0] >= t_overlap[1]:
            return 999.0
        
        # 3. Vector calculation
        v1 = (s1['p2'] - s1['p1']) / s1['duration']
        v2 = (s2['p2'] - s2['p1']) / s2['duration']
        
        p1_at_start = s1['p1'] + v1 * (t_overlap[0] - ts1)
        p2_at_start = s2['p1'] + v2 * (t_overlap[0] - ts2)
        
        dp = p1_at_start - p2_at_start
        dv = v1 - v2
        
        # 4. Minimize distance
        dv2 = np.dot(dv, dv)
        if dv2 > 1e-9:
            t_cpa = np.clip(-np.dot(dp, dv)/dv2, 0, t_overlap[1] - t_overlap[0])
        else:
            t_cpa = 0
        
        return np.linalg.norm(dp + dv * t_cpa)


# --- MODULE 2: COST ENGINE ---
class CostEngine:
    """Handles economic penalty logic."""
    
    @staticmethod
    def calculate_penalty(flight_dict, alt_shift, delay_sec):
        """
        Calculate cost for a given altitude shift and delay.
        
        Cost components:
        - Quadratic delay penalty (escalates with longer delays)
        - Altitude deviation from optimal range
        - Speed deviation from cruise range
        """
        if delay_sec < 0:
            return 1e18  # Cannot depart early
        
        pax = flight_dict['pax']
        cost = ((delay_sec / 60.0)**2) * pax
        
        for s in flight_dict['segments']:
            curr_alt = s['alt_orig'] + alt_shift
            
            # Altitude deviation cost: $5 per foot outside optimal range
            if curr_alt < s['opt_min']:
                cost += (s['opt_min'] - curr_alt) * 5
            elif curr_alt > s['opt_max']:
                cost += (curr_alt - s['opt_max']) * 5
            
            # Speed deviation cost
            speed = s['dist'] / (s['duration'] / 3600)
            if speed < s['cruise_min']:
                cost += (s['cruise_min'] - speed) * pax
            elif speed > s['cruise_max']:
                cost += (speed - s['cruise_max']) * pax
        
        return cost


# --- MODULE 3: CORE RESOLVER ---
class CostDriven4DResolver:
    """
    Main optimization engine for 4D flight path resolution.
    
    Uses local search with cost-driven optimization to resolve conflicts
    by adjusting altitude and departure time.
    """
    
    def __init__(self, min_sep_nm=5.0):
        self.min_sep_nm = min_sep_nm
        self.conflict_cost = 1e13  # Must dominate economic costs
        
        # Small maneuvers for fine-tuning
        self.maneuvers = [
            (0, 300),      # 5 min delay
            (0, 600),      # 10 min delay
            (2000, 0),     # 2000 ft up
            (-2000, 0),    # 2000 ft down
            (2000, 300),   # Combined
            (-2000, 300)
        ]
        
        # Larger maneuvers for escaping local minima
        self.larger_maneuvers = [
            (0, 1800),     # 30 min delay
            (0, 3600),     # 1 hour delay
            (4000, 0),     # 4000 ft up
            (6000, 0),     # 6000 ft up
            (-4000, 0),    # 4000 ft down
            (-6000, 0)     # 6000 ft down
        ]
    
    def resolve(self, schedule: FlightSchedule, iterations=30, 
                status=None) -> FlightSchedule:
        """
        Resolve conflicts in the flight schedule.
        
        Args:
            schedule: FlightSchedule to optimize
            iterations: Maximum number of optimization iterations
            status: Optional dict for status updates (for UI integration)
            
        Returns:
            FlightSchedule with optimized flight paths
        """
        if status is None:
            status = {}
        
        status['Message'] = "Starting optimization..."
        status['Total Iterations'] = iterations
        status['Current Iteration'] = 0
        
        # Convert to optimizer format
        flights_dict = schedule.to_optimizer_dict()
        active_neighborhood = self.maneuvers.copy()
        
        status['Message'] = "Optimizing..."
        
        for it in range(iterations):
            status['Current Iteration'] = it + 1
            
            # A. Build neighbor graph and count collisions
            potential_nb = defaultdict(set)
            f_list = list(flights_dict.values())
            collision_count = 0
            
            for i in range(len(f_list)):
                for j in range(i + 1, len(f_list)):
                    fa, fb = f_list[i], f_list[j]
                    
                    # Temporal filter: only check flights within 2 hours
                    if abs(fa['segments'][0]['t_start_orig'] - 
                          fb['segments'][0]['t_start_orig']) > 7200:
                        continue
                    
                    # Mark as potential neighbors
                    potential_nb[fa['acid']].add(fb['acid'])
                    potential_nb[fb['acid']].add(fa['acid'])
                    
                    # Count active collisions
                    if self._check_collision(fa, fb):
                        collision_count += 1
            
            # B. Optimization step - try to improve each flight
            changes_made = 0
            
            # Process flights in order of current cost (worst first)
            order = sorted(
                flights_dict.keys(), 
                key=lambda x: CostEngine.calculate_penalty(flights_dict[x], 0, 0), 
                reverse=True
            )
            
            for acid in order:
                f = flights_dict[acid]
                
                def get_total_local_cost(a_s, d_s):
                    """Calculate total cost including collisions with neighbors"""
                    score = CostEngine.calculate_penalty(f, a_s, d_s)
                    
                    # Add conflict penalties
                    for nb_id in potential_nb[acid]:
                        nb = flights_dict[nb_id]
                        if self._check_collision_custom(f, nb, a_s, d_s):
                            score += self.conflict_cost
                    
                    return score
                
                # Find best move in current neighborhood
                best_score = get_total_local_cost(f['current_alt_shift'], 
                                                  f['current_delay'])
                best_move = (f['current_alt_shift'], f['current_delay'])
                
                for m_a, m_d in active_neighborhood:
                    test_a = f['current_alt_shift'] + m_a
                    test_d = f['current_delay'] + m_d
                    current_move_score = get_total_local_cost(test_a, test_d)
                    
                    if current_move_score < best_score:
                        best_score = current_move_score
                        best_move = (test_a, test_d)
                
                # Apply best move if it improves the situation
                if best_move != (f['current_alt_shift'], f['current_delay']):
                    f['current_alt_shift'], f['current_delay'] = best_move
                    changes_made += 1
            
            # Progress logging
            print(f"Iteration {it+1:2d} | Conflicts: {collision_count:3d} | Changes: {changes_made:3d}")
            
            # Update status
            status['Active Conflicts'] = collision_count
            status['Total Conflicts'] = max(status.get('Total Conflicts', 0), 
                                           collision_count)
            status['Optimization Changes'] = (status.get('Optimization Changes', 0) + 
                                             changes_made)
            
            # C. Escape local minima logic
            if changes_made == 0 and collision_count > 0:
                print(">> STUCK: Expanding maneuver search space...")
                active_neighborhood = list(set(self.maneuvers + 
                                              self.larger_maneuvers))
            elif collision_count == 0:
                print(">> SUCCESS: All conflicts resolved.")
                break
        
        # Apply optimizations back to FlightSchedule
        return self._apply_optimizations(schedule, flights_dict)
    
    def _check_collision(self, f1, f2):
        """Check if two flights collide at current settings."""
        return self._check_collision_custom(
            f1, f2, 
            f1['current_alt_shift'], 
            f1['current_delay']
        )
    
    def _check_collision_custom(self, f1, f2, alt1, del1):
        """Check collision for hypothetical moves."""
        for s1 in f1['segments']:
            for s2 in f2['segments']:
                d = GeometryEngine.get_segment_cpa(
                    s1, s2, del1, alt1, 
                    f2['current_delay'], f2['current_alt_shift'], 
                    self.min_sep_nm
                )
                if d < self.min_sep_nm:
                    return True
        return False
    
    def _apply_optimizations(self, schedule: FlightSchedule, 
                            flights_dict: dict) -> FlightSchedule:
        """Apply optimization results back to FlightSchedule."""
        for flight in schedule.flights:
            if flight.acid in flights_dict:
                opt_data = flights_dict[flight.acid]
                flight.apply_optimization(
                    opt_data['current_alt_shift'],
                    opt_data['current_delay']
                )
        return schedule

if __name__ == "__main__":
    from backend.scheduler.models import FlightSchedule
    
    # Load flight schedule directly from JSON
    print("Loading flight schedule...")
    schedule = FlightSchedule.from_json_file('canadian_flights_1000.json')
    
    print(f"\n=== Initial Statistics ===")
    stats = schedule.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Initialize resolver
    print(f"\nInitializing resolver...")
    resolver = CostDriven4DResolver(min_sep_nm=5.0)
    
    # Resolve conflicts
    print(f"\n=== Starting Optimization ===")
    resolved_schedule = resolver.resolve(schedule, iterations=30)
    
    # Display results
    print(f"\n=== Final Statistics ===")
    final_stats = resolved_schedule.get_statistics()
    for key, value in final_stats.items():
        print(f"{key}: {value}")
    
    # Show collision pairs if any remain
    collisions = resolved_schedule.get_collision_pairs()
    if collisions:
        print(f"\n=== Remaining Collisions ===")
        for acid1, acid2, cpa in collisions[:10]:
            print(f"{acid1} <-> {acid2}: {cpa:.2f} nm")
    
    # Export to API format
    print(f"\n=== API Format Sample ===")
    api_output = resolved_schedule.to_api_dict()
    print(f"First flight: {api_output['1']}")