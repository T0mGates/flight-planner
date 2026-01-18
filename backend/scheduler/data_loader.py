# backend/scheduler/data_loader.py
"""
Simplified data loader - most functionality moved to FlightSchedule class.
This module now provides backward compatibility and utility functions.
"""

from backend.scheduler.models import FlightSchedule

# Main entry point - now just delegates to FlightSchedule
def generate_flight_schedule(file_path: str) -> FlightSchedule:
    """
    Load flight schedule from JSON file.
    
    This is now a thin wrapper around FlightSchedule.from_json_file()
    for backward compatibility.
    
    Args:
        file_path: Path to JSON file (relative to this module)
        
    Returns:
        FlightSchedule: Loaded and processed flight schedule
    """
    return FlightSchedule.from_json_file(file_path)


# For backward compatibility if anything was using these directly
def load_data(file_path: str):
    """Deprecated: Use FlightSchedule.from_json_file() instead"""
    import warnings
    warnings.warn(
        "load_data() is deprecated. Use FlightSchedule.from_json_file() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    import pandas as pd
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    abs_path = os.path.join(base_dir, file_path)
    df = pd.read_json(abs_path)
    df.columns = [col.replace(' ', '_') for col in df.columns]
    return df


if __name__ == "__main__":
    # Example usage
    schedule = generate_flight_schedule('canadian_flights_1000.json')
    print(f"Loaded {len(schedule)} flights")
    
    # Show statistics
    stats = schedule.get_statistics()
    print(f"\nSchedule Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Show first few rows as DataFrame
    print(f"\nFirst 5 segments:")
    print(schedule.to_dataframe().head())