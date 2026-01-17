import pandas as pd

def create_flight_constraints(df):
    """Create a constraints table for flights."""
    try:
        # Define altitude constraints with one Aircraft_Type per row
        altitude_constraints = [
            # Regional
            {
                'Aircraft_Type': 'Dash 8',
                'Min_altitude_ft': 22000,
                'Max_altitude_ft': 28000,
                'Optimal_altitude_min': 24000,
                'Optimal_altitude_max': 26000
            },
            {
                'Aircraft_Type': 'E195',
                'Min_altitude_ft': 22000,
                'Max_altitude_ft': 28000,
                'Optimal_altitude_min': 24000,
                'Optimal_altitude_max': 26000
            },
            # Narrow-body
            {
                'Aircraft_Type': '737',
                'Min_altitude_ft': 28000,
                'Max_altitude_ft': 39000,
                'Optimal_altitude_min': 33000,
                'Optimal_altitude_max': 37000
            },
            {
                'Aircraft_Type': 'A320',
                'Min_altitude_ft': 28000,
                'Max_altitude_ft': 39000,
                'Optimal_altitude_min': 33000,
                'Optimal_altitude_max': 37000
            },
            {
                'Aircraft_Type': 'A321',
                'Min_altitude_ft': 28000,
                'Max_altitude_ft': 39000,
                'Optimal_altitude_min': 33000,
                'Optimal_altitude_max': 37000
            },
            {
                'Aircraft_Type': 'A220',
                'Min_altitude_ft': 28000,
                'Max_altitude_ft': 39000,
                'Optimal_altitude_min': 33000,
                'Optimal_altitude_max': 37000
            },
            # Wide-body
            {
                'Aircraft_Type': '787',
                'Min_altitude_ft': 31000,
                'Max_altitude_ft': 43000,
                'Optimal_altitude_min': 37000,
                'Optimal_altitude_max': 41000
            },
            {
                'Aircraft_Type': '777',
                'Min_altitude_ft': 31000,
                'Max_altitude_ft': 43000,
                'Optimal_altitude_min': 37000,
                'Optimal_altitude_max': 41000
            },
            {
                'Aircraft_Type': 'A330',
                'Min_altitude_ft': 31000,
                'Max_altitude_ft': 43000,
                'Optimal_altitude_min': 37000,
                'Optimal_altitude_max': 41000
            },
            # Cargo
            {
                'Aircraft_Type': '767F',
                'Min_altitude_ft': 28000,
                'Max_altitude_ft': 41000,
                'Optimal_altitude_min': 35000,
                'Optimal_altitude_max': 39000
            },
            {
                'Aircraft_Type': '757F',
                'Min_altitude_ft': 28000,
                'Max_altitude_ft': 41000,
                'Optimal_altitude_min': 35000,
                'Optimal_altitude_max': 39000
            },
            {
                'Aircraft_Type': 'A300F',
                'Min_altitude_ft': 28000,
                'Max_altitude_ft': 41000,
                'Optimal_altitude_min': 35000,
                'Optimal_altitude_max': 39000
            }
        ]
        altitude_df = pd.DataFrame(altitude_constraints)

        # Speed constraints remain unchanged
        speed_constraints = [
            {
            'Aircraft_Type': 'Dash 8',
            'Max_cruise_Speed_knots': 360,
            'Min_cruise_Speed_knots': 360,
            'Min_Speed_knots': 310,
            'Max_Speed_knots': 410
            },
            {
            'Aircraft_Type': 'E195',
            'Max_cruise_Speed_knots': 450,
            'Min_cruise_Speed_knots': 420,
            'Min_Speed_knots': 370,
            'Max_Speed_knots': 500
            },
            {
            'Aircraft_Type': 'A220',
            'Max_cruise_Speed_knots': 450,
            'Min_cruise_Speed_knots': 420,
            'Min_Speed_knots': 370,
            'Max_Speed_knots': 500
            },
            {
            'Aircraft_Type': '737',
            'Max_cruise_Speed_knots': 485,
            'Min_cruise_Speed_knots': 465,
            'Min_Speed_knots': 415,
            'Max_Speed_knots': 505
            },
            {
            'Aircraft_Type': 'A320',
            'Max_cruise_Speed_knots': 485,
            'Min_cruise_Speed_knots': 465,
            'Min_Speed_knots': 415,
            'Max_Speed_knots': 505
            },
            {
            'Aircraft_Type': 'A321',
            'Max_cruise_Speed_knots': 485,
            'Min_cruise_Speed_knots': 465,
            'Min_Speed_knots': 415,
            'Max_Speed_knots': 505
            },
            {
            'Aircraft_Type': '787',
            'Max_cruise_Speed_knots': 505,
            'Min_cruise_Speed_knots': 480,
            'Min_Speed_knots': 430,
            'Max_Speed_knots': 505
            },
            {
            'Aircraft_Type': '777',
            'Max_cruise_Speed_knots': 505,
            'Min_cruise_Speed_knots': 480,
            'Min_Speed_knots': 430,
            'Max_Speed_knots': 505
            },
            {
            'Aircraft_Type': 'A330',
            'Max_cruise_Speed_knots': 505,
            'Min_cruise_Speed_knots': 480,
            'Min_Speed_knots': 430,
            'Max_Speed_knots': 505
            },
            {
            'Aircraft_Type': '767F',
            'Max_cruise_Speed_knots': 480,
            'Min_cruise_Speed_knots': 460,
            'Min_Speed_knots': 410,
            'Max_Speed_knots': 505
            },
            {
            'Aircraft_Type': '757F',
            'Max_cruise_Speed_knots': 480,
            'Min_cruise_Speed_knots': 460,
            'Min_Speed_knots': 410,
            'Max_Speed_knots': 505
            },
            {
            'Aircraft_Type': 'A300F',
            'Max_cruise_Speed_knots': 480,
            'Min_cruise_Speed_knots': 460,
            'Min_Speed_knots': 410,
            'Max_Speed_knots': 505
            }
        ]
        speed_df = pd.DataFrame(speed_constraints)
        return altitude_df, speed_df
    except Exception as e:
        print(f"An error occurred while creating flight constraints: {e}")
        return pd.DataFrame(), pd.DataFrame()
