import pandas as pd

from backend.scheduler.models import FlightSchedule

import pandas as pd

def compare_schedules(new_schedule, old_schedule):
    """
    Compares two flight schedules, analyzing delays and collision improvements.
    
    Args:
        new_schedule (pd.DataFrame): Optimized schedule.
        old_schedule (pd.DataFrame): Original schedule.
        
    Returns:
        tuple: (top_delays, merged_df, delay_count, avg_delay, new_collisions, old_collisions)
    """

    # Helper to clean and prepare DataFrames
    def prepare_df(data):
        if not isinstance(data, pd.DataFrame):
            # orient='index' handles { ACID: {data} }
            df = pd.DataFrame.from_dict(data, orient='index')
        else:
            df = data.copy()
            
        # If 'ACID' isn't a column, it's likely the index. 
        # Move it to a column without using reset_index() naming
        if 'ACID' not in df.columns:
            df.insert(0, 'ACID', df.index)
            
        return df
    
    df_new = prepare_df(new_schedule)
    df_old = prepare_df(old_schedule)

    # 1. Merge the schedules
    # Guaranteed to have 'ACID' as a column
    merged = pd.merge(
        df_new, 
        df_old, 
        on=['ACID', 'departure_airport', 'arrival_airport', 'route'], 
        suffixes=('_opt', '_orig')
    )

    # 2. Calculate time differences (Positive means the optimized flight is LATER than original)
    merged['departure_time_diff'] = merged['departure_time_opt'] - merged['departure_time_orig']

    # 3. Identify delays
    # In scheduling, a 'delay' is often relative to the original plan
    merged['was_delayed'] = merged['departure_time_diff'] > 0
    delay_count = int(merged['was_delayed'].sum())
    avg_delay = merged['departure_time_diff'].mean()

    # 4. Extract Top 10 most significant schedule shifts
    top_delays = merged.nlargest(10, 'departure_time_diff')[
        ['ACID', 'departure_airport', 'arrival_airport', 'departure_time_orig', 'departure_time_opt', 'departure_time_diff']
    ].to_dict(orient='records')
    

    # 5. Collision Analysis
    # Note: We pass the original DataFrames to your FlightSchedule class
    new_flight_schedule = FlightSchedule.from_api_dict(new_schedule, needs_airport_translation=True)
    old_flight_schedule = FlightSchedule.from_api_dict(old_schedule, needs_airport_translation=True)
    
    new_collisions = new_flight_schedule.count_collisions()
    old_collisions = old_flight_schedule.count_collisions()


    # Transforming into the dictionary
    formatted_dict = {
        "most_notable_delays": top_delays,
        "number_of_delays": delay_count,
        #"flights": flights,
        "mean_delay": avg_delay,
        #"optimization_changes": changes,
        "new_num_conflicts": new_collisions, 
        "old_num_conflicts": old_collisions,  
        "old_flight_schedule": old_schedule,
        "optimized_flight_schedule": new_schedule
    }
    
    return formatted_dict

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