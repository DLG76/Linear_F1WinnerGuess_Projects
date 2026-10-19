import numpy as np
import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import TARGET_YEAR


LAYOUT_CHANGE_YEAR = 2023


SCORES_2023_PLUS = np.array([
    24,  # Corner 1  (Heavy braking zone)
    15,  # Corner 2  (chaos)
    1,   # Corner 3
    1,   # Corner 4
    1,   # Corner 5  (Critical exit to Raffles Blvd)
    28,  # Corner 6  (High-speed DRS zone )
    4,   # Corner 7  (Memorial heavy braking)
    1,   # Corner 8
    10,  # Corner 9  
    1,   # Corner 10 (Singapore Sling)
    1,   # Corner 11
    30,  # Corner 12 (RUS 10.0, ANT/NOR strong)
    1,   # Corner 13 (Hairpin exit)
    25,  # Corner 14 (Connaught heavy braking & exit)
    18,  # Corner 15 
    1,   # Corner 16 (Sector 3 braking)
    14,  # Corner 17 (Chicane traction exit)
    1,   # Corner 18
    8    # Corner 19 (Final corner to Pit Straight)
], dtype=float)

SCORES_PRE_2023 = np.array([
    2,   # Corner 1   Sheares corners 1-3: chaos at the start
    2,   # Corner 2   Sheares corners 1-3
    2,   # Corner 3   Sheares corners 1-3
    11,  # Corner 4   737 m.
    1,   # Corner 5   
    30,  # Corner 6    
    2,   # Corner 7   Memorial Corner: main overtaking spot
    15,  # Corner 8   
    1,   # Corner 9   
    10,  # Corner 10  Singapore Sling: most dangerous
    1,   # Corner 11  
    1,   # Corner 12  
    2,   # Corner 13  Merlion Hairpin / Anderson Bridge: overtaking
    1,   # Corner 14  
    1,   # Corner 15  kept low on purpose: P-spread ~6 (normal corner: ~0.9), one corner
         #            would decide the whole ranking
    3,   # Corner 16  Bay Grandstand 16-19
    10,  # Corner 17  Bay Grandstand 16-19
    2,   # Corner 18  Bay Grandstand 16-19
    2,   # Corner 19  Bay Grandstand 16-19
    1,   # Corner 20 
    1,   # Corner 21 
    1,   # Corner 22  
    12   # Corner 23  4955 m, last corner before the start/finish straight
         #                   
], dtype=float)

WEIGHT_SETS = {
    'pre_2023': SCORES_PRE_2023,
    'post_2023': SCORES_2023_PLUS,
}

layout = 'post_2023' if TARGET_YEAR >= LAYOUT_CHANGE_YEAR else 'pre_2023'
corner_scores = WEIGHT_SETS[layout]
print(f"TARGET_YEAR {TARGET_YEAR} -> using weight set '{layout}' ({len(corner_scores)} corners)")

# safety check: the data's corner count must match the chosen set
n_corners = len(pd.read_csv(f'singapore_{TARGET_YEAR}_corners.csv'))
if n_corners != len(corner_scores):
    print(f"WARNING: {TARGET_YEAR} data has {n_corners} corners but set '{layout}' has "
          f"{len(corner_scores)}. Using equal weights for every corner.")
    corner_scores = np.ones(n_corners)

A_matrix = np.outer(corner_scores, 1.0 / corner_scores)
eigenvalues, eigenvectors = np.linalg.eig(A_matrix)
max_idx = np.argmax(eigenvalues.real)
w_vector = np.abs(eigenvectors[:, max_idx].real)
w_vector = w_vector / np.sum(w_vector)

w_df = pd.DataFrame({
    'Corner': [f"Corner_{i}" for i in range(1, n_corners + 1)],
    'AHP_Score': corner_scores.astype(int),
    'Weight_w': np.round(w_vector, 4)
})

w_df.to_csv('corner_weights_w.csv', index=False)
print(w_df.to_string(index=False))
print("\n-> บันทึกไฟล์ corner_weights_w.csv สำเร็จ!")