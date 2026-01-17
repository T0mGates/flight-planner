from backend.scheduler.SpacetimeOptimizer import CostEngine, GeometryEngine

import numpy as np

def test_resolver_units():
    # 1. Test Geometry: Direct Head-on collision
    s1 = {'p1': np.array([0,0,0]), 'p2': np.array([10,0,0]), 't_start_orig': 0, 'duration': 10, 'alt_orig': 30000}
    s2 = {'p1': np.array([10,0,0]), 'p2': np.array([0,0,0]), 't_start_orig': 0, 'duration': 10, 'alt_orig': 30000}
    dist = GeometryEngine.get_segment_cpa(s1, s2, 0, 0, 0, 0, 5.0)
    assert dist < 1.0, "Geometry Engine failed to detect head-on collision"
    
    # 2. Test Cost Engine: Delay penalty
    flight_mock = {'pax': 100, 'segments': []}
    cost_0 = CostEngine.calculate_penalty(flight_mock, 0, 0)
    cost_10min = CostEngine.calculate_penalty(flight_mock, 0, 600)
    assert cost_10min == (10**2) * 100, "Cost Engine calculated delay penalty incorrectly"
    
    # 3. Test Cost Engine: Hard Departure Constraint
    assert CostEngine.calculate_penalty(flight_mock, 0, -10) > 1e14, "Failed to penalize early departure"
    
    print("All unit tests passed!")

test_resolver_units()