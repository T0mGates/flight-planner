import pandas as pd

from backend.scheduler.models import FlightSchedule

def compare_schedules(new_schedule, old_schedule):
    """
    Compares two flight schedules and returns a similarity score.
    
    Args:
        new_schedule (pd.DataFrame): The first flight schedule.
        old_schedule (pd.DataFrame): The second flight schedule.
        
    Returns:
        float: A similarity score between 0 and 1.
    """
    
    #FORMAT (WILL BE IN DATAFRAME FORM)
    """
    {"departure_airport":"43.68N/79.63W","arrival_airport":"44.55N/75.22W","route":"44.55N/75.22W","ACID":"ACA101","plane_type":"767F","is_cargo":true,"aircraft_speed":[480.00000000008544,479.99999999999045],"departure_time":1767822240,"altitude":[26000.0,26000.0],"passengers":0,"id":1},
    """
    
    # Merge the schedules on the specified columns
    merged = pd.merge(new_schedule, old_schedule, on=['departure_airport', 'arrival_airport', 'route', 'ACID', 'plane_type', 'is_cargo'], suffixes=('_1', '_2'))

    # Drop columns from old_schedule that are also in new_schedule (except the merge keys)
    cols_to_drop = [col + '_2' for col in new_schedule.columns if col not in ['departure_airport', 'arrival_airport', 'route', 'ACID', 'plane_type', 'is_cargo'] and col in old_schedule.columns]
    merged = merged.drop(columns=cols_to_drop)
    
    # Get difference in departure_time
    merged['departure_time_diff'] = merged['departure_time_1'] - merged['departure_time_2']
    
    
    # Get count of delayed flights
    merged['was_delayed'] = merged['departure_time_diff'] > 0
    delayed = merged['was_delayed'].sum()
        
    # Make table of top 10 delays
    top_delays = merged.nlargest(10, 'departure_time_diff')[['departure_airport', 'arrival_airport', 'route', 'ACID', 'plane_type', 'is_cargo', 'departure_time_diff']]
    
    # Create flight schedules from dataframes
    new_flight_schedule = FlightSchedule.from_compact_dataframe(new_schedule)
    old_flight_schedule = FlightSchedule.from_compact_dataframe(old_schedule)
    
    # Get number of collisions in each schedule
    new_collisions = new_flight_schedule.count_collisions()
    old_collisions = old_flight_schedule.count_collisions()
    
    # Returns: Most notable delays, count of delays, average delay, new collision count, old collision count
    
    return top_delays, merged, delayed, merged['was_delayed'].mean(), new_collisions, old_collisions

def compare_by_acids(new_schedule, old_schedule):
    """
    Compares two flight schedules for specific ACIDs and returns a similarity score.
    
    Args:
        new_schedule (pd.DataFrame): The first flight schedule.
        old_schedule (pd.DataFrame): The second flight schedule.
    
    Returns:
        dict: A dictionary with ACID as keys and comparison results as values.
    """
    
    print("Comparing flight schedules by ACID...")
    print(f"New schedule flights: {new_schedule}")
    print(f"Old schedule flights: {old_schedule}")
    
    merged = pd.merge(new_schedule, old_schedule, on='ACID', suffixes=('_1', '_2'))
    comparison_results = {}
    for _, row in merged.iterrows():
        acid = row['ACID']
        departure_time_diff = row['departure_time_1'] - row['departure_time_2']
        comparison_results[acid] = {
            'departure_time_diff': departure_time_diff,
            'was_delayed': departure_time_diff > 0,
            'average_speed_diff': (sum(row['aircraft_speed_1'])/len(row['aircraft_speed_1'])) - (sum(row['aircraft_speed_2'])/len(row['aircraft_speed_2'])),
            'average_altitude_diff': (sum(row['altitude_1'])/len(row['altitude_1'])) - (sum(row['altitude_2'])/len(row['altitude_2']))
        }    
        comparison_results[acid]['has_differences'] = any([
            comparison_results[acid]['departure_time_diff'] != 0,
            comparison_results[acid]['average_speed_diff'] != 0,
            comparison_results[acid]['average_altitude_diff'] != 0
        ])
    
    return comparison_results