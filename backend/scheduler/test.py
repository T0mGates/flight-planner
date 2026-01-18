# example_usage.py - Complete usage examples

from backend.scheduler.models import FlightSchedule
from backend.scheduler.resolver import CostDriven4DResolver

# ============================================================
# EXAMPLE 1: Load and analyze a flight schedule
# ============================================================

def example_load_and_analyze():
    """Load flights from JSON and get statistics"""
    print("=== EXAMPLE 1: Load and Analyze ===\n")
    
    # Load directly from JSON file
    schedule = FlightSchedule.from_json_file('canadian_flights_1000.json')
    
    # Get basic info
    print(f"Loaded {len(schedule)} flights")
    
    # Get detailed statistics
    stats = schedule.get_statistics()
    print(f"\nStatistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Access individual flights
    flight = schedule.get_flight('AAL123')  # Example ACID
    if flight:
        print(f"\nFlight {flight.acid}:")
        print(f"  Route: {flight.departure_airport} -> {flight.arrival_airport}")
        print(f"  Segments: {len(flight.segments)}")
        print(f"  Total distance: {flight.total_distance_nm:.2f} nm")
        print(f"  Duration: {flight.total_duration_sec / 3600:.2f} hours")


# ============================================================
# EXAMPLE 2: Check for collisions
# ============================================================

def example_collision_detection():
    """Detect and analyze collisions"""
    print("\n=== EXAMPLE 2: Collision Detection ===\n")
    
    schedule = FlightSchedule.from_json_file('canadian_flights_1000.json')
    
    # Count total collisions
    collision_count = schedule.count_collisions(min_separation_nm=5.0)
    print(f"Total collision pairs: {collision_count}")
    
    # Get detailed collision information
    collisions = schedule.get_collision_pairs(min_separation_nm=5.0)
    
    print(f"\nFirst 5 collision pairs:")
    for acid1, acid2, cpa in collisions[:5]:
        f1 = schedule.get_flight(acid1)
        f2 = schedule.get_flight(acid2)
        print(f"  {acid1} <-> {acid2}")
        print(f"    Closest approach: {cpa:.2f} nm")
        print(f"    {f1.departure_airport} -> {f1.arrival_airport}")
        print(f"    {f2.departure_airport} -> {f2.arrival_airport}")


# ============================================================
# EXAMPLE 3: Resolve conflicts
# ============================================================

def example_resolve_conflicts():
    """Run the optimizer to resolve conflicts"""
    print("\n=== EXAMPLE 3: Resolve Conflicts ===\n")
    
    # Load schedule
    schedule = FlightSchedule.from_json_file('canadian_flights_1000.json')
    
    # Check initial collisions
    initial_collisions = schedule.count_collisions()
    print(f"Initial collisions: {initial_collisions}")
    
    # Create resolver and optimize
    resolver = CostDriven4DResolver(min_sep_nm=5.0)
    status = {}
    
    print("\nOptimizing...")
    resolved_schedule = resolver.resolve(schedule, iterations=30, status=status)
    
    # Check final collisions
    final_collisions = resolved_schedule.count_collisions()
    print(f"\nFinal collisions: {final_collisions}")
    print(f"Resolved: {initial_collisions - final_collisions} collision pairs")
    
    # Show optimization summary
    print(f"\nOptimization summary:")
    print(f"  Total changes made: {status.get('Optimization Changes', 0)}")
    print(f"  Iterations used: {status.get('Current Iteration', 0)}")


# ============================================================
# EXAMPLE 4: Export to different formats
# ============================================================

def example_export_formats():
    """Export schedule to different formats"""
    print("\n=== EXAMPLE 4: Export Formats ===\n")
    
    schedule = FlightSchedule.from_json_file('canadian_flights_1000.json')
    
    # Export to API format (for FastAPI)
    api_dict = schedule.to_api_dict()
    print("API format (first flight):")
    print(api_dict['1'])
    
    # Export to DataFrame (for analysis)
    df = schedule.to_dataframe()
    print(f"\nDataFrame shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Export to optimizer format (internal)
    opt_dict = schedule.to_optimizer_dict()
    print(f"\nOptimizer format contains {len(opt_dict)} flights")


# ============================================================
# EXAMPLE 5: Modify and re-optimize
# ============================================================

def example_modify_schedule():
    """Modify flights and re-optimize"""
    print("\n=== EXAMPLE 5: Modify and Re-optimize ===\n")
    
    schedule = FlightSchedule.from_json_file('canadian_flights_1000.json')
    
    # Get a flight and modify it
    flight = schedule.flights[0]
    print(f"Original departure: {flight.departure_time}")
    
    # Apply a manual adjustment (e.g., delay by 30 minutes)
    flight.apply_optimization(alt_shift_ft=0, delay_sec=1800)
    print(f"Modified departure: {flight.departure_time}")
    
    # Re-optimize the entire schedule
    resolver = CostDriven4DResolver(min_sep_nm=5.0)
    resolved = resolver.resolve(schedule, iterations=10)
    
    print(f"Re-optimized collisions: {resolved.count_collisions()}")


# ============================================================
# EXAMPLE 6: Query flight position at specific time
# ============================================================

def example_query_position():
    """Query where a flight is at a specific time"""
    print("\n=== EXAMPLE 6: Query Flight Position ===\n")
    
    from datetime import datetime, timedelta
    
    schedule = FlightSchedule.from_json_file('canadian_flights_1000.json')
    
    flight = schedule.flights[0]
    
    # Get position 30 minutes after departure
    query_time = flight.departure_time + timedelta(minutes=30)
    position = flight.get_position_at_time(query_time)
    
    if position:
        ecef_pos, altitude = position
        print(f"Flight {flight.acid} at {query_time}:")
        print(f"  ECEF position: {ecef_pos}")
        print(f"  Altitude: {altitude:.0f} ft")
    else:
        print(f"Flight not active at {query_time}")


# ============================================================
# EXAMPLE 7: Complete workflow
# ============================================================

def example_complete_workflow():
    """Full pipeline: load, analyze, optimize, export"""
    print("\n=== EXAMPLE 7: Complete Workflow ===\n")
    
    # 1. Load
    print("1. Loading schedule...")
    schedule = FlightSchedule.from_json_file('canadian_flights_1000.json')
    print(f"   Loaded {len(schedule)} flights")
    
    # 2. Analyze
    print("\n2. Analyzing conflicts...")
    initial_stats = schedule.get_statistics()
    print(f"   Initial collisions: {initial_stats['collisions']}")
    
    # 3. Optimize
    print("\n3. Optimizing...")
    resolver = CostDriven4DResolver(min_sep_nm=5.0)
    status = {}
    resolved = resolver.resolve(schedule, iterations=30, status=status)
    
    # 4. Validate
    print("\n4. Validating results...")
    final_stats = resolved.get_statistics()
    print(f"   Final collisions: {final_stats['collisions']}")
    print(f"   Changes made: {status.get('Optimization Changes', 0)}")
    
    # 5. Export
    print("\n5. Exporting...")
    api_output = resolved.to_api_dict()
    print(f"   Exported {len(api_output)} flights to API format")
    
    # 6. Save to file (optional)
    import json
    with open('resolved_schedule.json', 'w') as f:
        json.dump(api_output, f, indent=2)
    print("   Saved to resolved_schedule.json")
    
    return resolved


# ============================================================
# Run all examples
# ============================================================

if __name__ == "__main__":
    # Run individual examples
    example_load_and_analyze()
    example_collision_detection()
    example_resolve_conflicts()
    example_export_formats()
    example_modify_schedule()
    example_query_position()
    
    # Or run the complete workflow
    # resolved_schedule = example_complete_workflow()