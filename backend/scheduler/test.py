import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from backend.scheduler.main import detect_collisions

def create_test_data():
    """
    Create test cases with known outcomes for collision detection.
    """
    
    # Coordinates are now embedded in waypoint names as "lat/lon" format
    # Using format like "45.0N/75.0W"
    # We'll use simple coordinates for testing
    
    base_time = datetime(2024, 1, 1, 12, 0, 0)
    
    # Test Case 1: HEAD-ON COLLISION
    # Two aircraft flying directly at each other on same path, same altitude
    test1_waypoints = pd.DataFrame([
        {
            'ACID': 'TEST001',
            'segment_number': 1,
            'from': '45.0N/75.0W',  # Ottawa area
            'to': '45.0N/74.0W',    # 1 degree east
            'estimated_departure_time': base_time,
            'estimated_arrival_time': base_time + timedelta(minutes=60),
            'Plane_type': 'B737',
        },
        {
            'ACID': 'TEST002',
            'segment_number': 1,
            'from': '45.0N/74.0W',  # 1 degree east
            'to': '45.0N/75.0W',    # Ottawa area (flying opposite direction)
            'estimated_departure_time': base_time,
            'estimated_arrival_time': base_time + timedelta(minutes=60),
            'Plane_type': 'A320',
        }
    ])
    
    # Test Case 2: PERPENDICULAR CROSSING
    # Two aircraft crossing paths at 90 degrees, same altitude
    test2_waypoints = pd.DataFrame([
        {
            'ACID': 'TEST003',
            'segment_number': 1,
            'from': '45.0N/74.0W',
            'to': '45.0N/76.0W',  # Flying east
            'estimated_departure_time': base_time,
            'estimated_arrival_time': base_time + timedelta(minutes=60),
            'Plane_type': 'B737',
        },
        {
            'ACID': 'TEST004',
            'segment_number': 1,
            'from': '44.0N/75W',  # North of crossing point
            'to': '46.0N/75W',    # South of crossing point (flying south)
            'estimated_departure_time': base_time + timedelta(minutes=4),
            'estimated_arrival_time': base_time + timedelta(minutes=64),
            'Plane_type': 'A320',
        }
    ])
    
    # Test Case 3: SAFE - Different altitudes
    # Same path, but separated by altitude (using different plane types with different optimal altitudes)
    test3_waypoints = pd.DataFrame([
        {
            'ACID': 'TEST005',
            'segment_number': 1,
            'from': '45.0N/75.0W',
            'to': '45.0N/74.0W',
            'estimated_departure_time': base_time,
            'estimated_arrival_time': base_time + timedelta(minutes=60),
            'Plane_type': 'B737_LOW',  # Will have lower altitude range
        },
        {
            'ACID': 'TEST006',
            'segment_number': 1,
            'from': '45.0N/75.0W',
            'to': '45.0N/74.0W',
            'estimated_departure_time': base_time,
            'estimated_arrival_time': base_time + timedelta(minutes=60),
            'Plane_type': 'A320_HIGH',  # Will have higher altitude range
        }
    ])
    
    # Test Case 4: SAFE - Different times
    # Same path, but no time overlap
    test4_waypoints = pd.DataFrame([
        {
            'ACID': 'TEST007',
            'segment_number': 1,
            'from': '45.0N/75.0W',
            'to': '45.0N/74.0W',
            'estimated_departure_time': base_time,
            'estimated_arrival_time': base_time + timedelta(minutes=30),
            'Plane_type': 'B737',
        },
        {
            'ACID': 'TEST008',
            'segment_number': 1,
            'from': '45.0N/75.0W',
            'to': '45.0N/74.0W',
            'estimated_departure_time': base_time + timedelta(minutes=35),
            'estimated_arrival_time': base_time + timedelta(minutes=65),
            'Plane_type': 'A320',
        }
    ])
    
    # Test Case 5: PARALLEL PATHS - SAFE
    # Flying parallel, separated by more than 5nm
    test5_waypoints = pd.DataFrame([
        {
            'ACID': 'TEST009',
            'segment_number': 1,
            'from': '45.0N/75.0W',
            'to': '45.0N/74.0W',
            'estimated_departure_time': base_time,
            'estimated_arrival_time': base_time + timedelta(minutes=60),
            'Plane_type': 'B737',
        },
        {
            'ACID': 'TEST010',
            'segment_number': 1,
            'from': '46.0N/75.0W',  # 1 degree north (about 60nm)
            'to': '46.0N/74.0W',
            'estimated_departure_time': base_time,
            'estimated_arrival_time': base_time + timedelta(minutes=60),
            'Plane_type': 'A320',
        }
    ])
    
    # Test Case 6: NEAR MISS - Just inside threshold
    # Two aircraft pass very close (within 5nm and 2000ft)
    test6_waypoints = pd.DataFrame([
        {
            'ACID': 'TEST011',
            'segment_number': 1,
            'from': '45.0N/75.0W',
            'to': '45.05N/74.95W',  # Short segment northeast
            'estimated_departure_time': base_time,
            'estimated_arrival_time': base_time + timedelta(minutes=30),
            'Plane_type': 'B737',
        },
        {
            'ACID': 'TEST012',
            'segment_number': 1,
            'from': '45.05N/75.0W',  # Slightly north
            'to': '45.0N/74.95W',    # Converging paths
            'estimated_departure_time': base_time,
            'estimated_arrival_time': base_time + timedelta(minutes=30),
            'Plane_type': 'A320',
        }
    ])
    
    # Create altitude lookup with Optimal_altitude columns
    altitude_df = pd.DataFrame([
        {
            'Aircraft_Type': 'B737', 
            'Min_altitude_ft': 0, 
            'Max_altitude_ft': 41000,
            'Optimal_altitude_min': 30000,
            'Optimal_altitude_max': 31000
        },
        {
            'Aircraft_Type': 'A320', 
            'Min_altitude_ft': 0, 
            'Max_altitude_ft': 39000,
            'Optimal_altitude_min': 30000,
            'Optimal_altitude_max': 31000
        },
        {
            'Aircraft_Type': 'B737_LOW',  # For altitude separation test
            'Min_altitude_ft': 0, 
            'Max_altitude_ft': 41000,
            'Optimal_altitude_min': 25000,
            'Optimal_altitude_max': 27000
        },
        {
            'Aircraft_Type': 'A320_HIGH',  # For altitude separation test
            'Min_altitude_ft': 0, 
            'Max_altitude_ft': 39000,
            'Optimal_altitude_min': 35000,
            'Optimal_altitude_max': 37000
        },
    ])
    
    test_cases = [
        {
            'name': 'Test 1: Head-on Collision',
            'waypoints': test1_waypoints,
            'expected': 'COLLISION - should detect collision at midpoint',
            'expected_collisions': 1,
        },
        {
            'name': 'Test 2: Perpendicular Crossing',
            'waypoints': test2_waypoints,
            'expected': 'COLLISION - paths cross at point E',
            'expected_collisions': 1,
        },
        {
            'name': 'Test 3: Safe - Vertical Separation',
            'waypoints': test3_waypoints,
            'expected': 'SAFE - 5000ft vertical separation',
            'expected_collisions': 0,
        },
        {
            'name': 'Test 4: Safe - Temporal Separation',
            'waypoints': test4_waypoints,
            'expected': 'SAFE - no time overlap',
            'expected_collisions': 0,
        },
        {
            'name': 'Test 5: Safe - Parallel Paths',
            'waypoints': test5_waypoints,
            'expected': 'SAFE - parallel, >60nm apart',
            'expected_collisions': 0,
        },
        {
            'name': 'Test 6: Near Miss',
            'waypoints': test6_waypoints,
            'expected': 'COLLISION - converging at point E with overlapping altitudes',
            'expected_collisions': 1,
        },
    ]
    
    return test_cases, altitude_df


def run_tests(detect_collisions_func):
    """
    Run all test cases and report results.
    
    Args:
        detect_collisions_func: The detect_collisions function to test
    """
    test_cases, altitude_df = create_test_data()
    
    print("="*80)
    print("RUNNING COLLISION DETECTION TESTS")
    print("="*80)
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{test['name']}")
        print(f"Expected: {test['expected']}")
        print("-" * 80)
        
        try:
            # Run collision detection (no coords_lookup needed)
            collisions = detect_collisions_func(
                test['waypoints'],
                altitude_df,
                horizontal_threshold_nm=5.0,
                vertical_threshold_ft=2000.0
            )
            
            num_collisions = len(collisions)
            
            print(f"Detected: {num_collisions} collision(s)")
            
            if num_collisions > 0:
                print("\nCollision Details:")
                for _, col in collisions.iterrows():
                    print(f"  - {col['ACID_1']} vs {col['ACID_2']}")
                    print(f"    CPA Distance: {col['cpa_distance_nm']:.2f} nm")
                    print(f"    Vertical Sep: {col['min_vertical_separation_ft']:.0f} ft")
                    print(f"    CPA Time: {col['cpa_time']}")
            
            # Check if result matches expectation
            if num_collisions == test['expected_collisions']:
                print(f"\n✓ PASSED")
                passed += 1
            else:
                print(f"\n✗ FAILED - Expected {test['expected_collisions']}, got {num_collisions}")
                failed += 1
                
        except Exception as e:
            print(f"\n✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*80)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("="*80)
    
    return passed, failed


# Example of how to use:
if __name__ == "__main__":
    # Import your detect_collisions function
    # from your_module import detect_collisions
    
    # Run tests
    run_tests(detect_collisions)