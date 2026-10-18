import pandas as pd
import numpy as np
import os

TARGET_YEAR = int(os.environ.get('F1_YEAR', 2026))

data_file = f'singapore_q_top7_{TARGET_YEAR}_data.csv'
corners_file = f'singapore_{TARGET_YEAR}_corners.csv'

telemetry_df = pd.read_csv(data_file)
corners_df = pd.read_csv(corners_file)

drivers = telemetry_df['Driver'].unique().tolist()
print(f"create Matrix P ปี {TARGET_YEAR} for: {drivers}")

offset = 45.0
apices = corners_df['Distance'].values
start_dists, end_dists = [], []

for i in range(len(apices)):
    if i > 0 and (apices[i] - offset) < (apices[i-1] + offset):
        start_dists.append((apices[i-1] + apices[i]) / 2.0)
    else:
        start_dists.append(apices[i] - offset)
        
    if i < len(apices) - 1 and (apices[i] + offset) > (apices[i+1] - offset):
        end_dists.append((apices[i] + apices[i+1]) / 2.0)
    else:
        end_dists.append(apices[i] + offset)

corners_df['Start_Dist'] = start_dists
corners_df['End_Dist'] = end_dists

P_matrix = np.zeros((19, len(drivers)))
W_SPEED = 5.0
W_THROTTLE = 5.0

for i, row in corners_df.iterrows():
    c_start, c_end = row['Start_Dist'], row['End_Dist']
    interp_grid = np.linspace(c_start, c_end, 20)
    
    apex_speeds, avg_speeds, throttle_vectors = {}, {}, {}
    
    for d in drivers:
        d_df = telemetry_df[(telemetry_df['Driver'] == d) & 
                            (telemetry_df['Distance'] >= c_start) & 
                            (telemetry_df['Distance'] <= c_end)]
        if len(d_df) > 1:
            apex_speeds[d] = d_df['Speed'].min()
            avg_speeds[d] = d_df['Speed'].mean()
            throttle_vectors[d] = np.interp(interp_grid, d_df['Distance'], d_df['Throttle'])
        else:
            apex_speeds[d], avg_speeds[d] = 0.0, 0.0
            throttle_vectors[d] = np.zeros(20)
            
    v_ideal = max(apex_speeds.values())
    best_driver = max(avg_speeds, key=avg_speeds.get)
    t_best = throttle_vectors[best_driver]
    
    for j, d in enumerate(drivers):
        dist_euclid = np.sqrt((v_ideal - apex_speeds[d])**2)
        score_speed = W_SPEED * (1.0 - (dist_euclid / v_ideal)) if v_ideal > 0 else 0.0
        
        t_drv = throttle_vectors[d]
        norm_drv, norm_best = np.linalg.norm(t_drv), np.linalg.norm(t_best)
        cos_sim = np.dot(t_drv, t_best) / (norm_drv * norm_best) if (norm_drv > 0 and norm_best > 0) else 0.0
        score_throttle = W_THROTTLE * cos_sim
        
        P_matrix[i, j] = round(score_speed + score_throttle, 4)

P_df = pd.DataFrame(P_matrix, columns=drivers, index=[f"Corner_{k}" for k in range(1, 20)])
P_df.to_csv('performance_matrix_P.csv')
print(P_df)
print("-> save performance_matrix_P.csv success")