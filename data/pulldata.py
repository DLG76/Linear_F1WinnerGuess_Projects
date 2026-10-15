import fastf1
import pandas as pd
import os

if not os.path.exists('cache'):
    os.makedirs('cache')
fastf1.Cache.enable_cache('cache')

print("pulling Session Singapore 2025...")
session = fastf1.get_session(2025, 'Singapore', 'Q')
session.load()
    
print("pulling 19 corners")
circuit_info = session.get_circuit_info()
corners_df = pd.DataFrame({
    'Corner_Number': circuit_info.corners['Number'],
    'Distance': circuit_info.corners['Distance']
})
corners_df.to_csv('singapore_2025_corners.csv', index=False)
print("save singapore_2025_corners.csv success")

top_7_drivers = ['ANT', 'RUS', 'HAM', 'VER', 'LEC', 'NOR', 'PIA']
print(f"\ndrivers: {top_7_drivers}")

all_telemetry_data = pd.DataFrame()

for driver in top_7_drivers:
    try:
        fastest_lap = session.laps.pick_driver(driver).pick_fastest()  
        if pd.isna(fastest_lap['Time']):
            print(f"skip {driver}: not found")
            continue

        telemetry = fastest_lap.get_telemetry()
        
        df = telemetry[['Distance', 'Speed', 'Throttle']].copy()
        df['Driver'] = driver
        
        all_telemetry_data = pd.concat([all_telemetry_data, df], ignore_index=True)
        print(f"pull {driver} succes amount: {len(df)} vector")
        
    except Exception as e:
        print(f"Error {driver}: {e}")

print("\n All done")
print(f"vectors: {len(all_telemetry_data)}")

all_telemetry_data.to_csv('singapore_q_top7_2025_data.csv', index=False)
print("-> save singapore_q_top7_2025_data.csv success")