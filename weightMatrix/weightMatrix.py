import numpy as np
import pandas as pd

corner_scores = np.array([
    1,   # Corner 1
    1,   # Corner 2
    9,   # Corner 3  (Technical flow exit)
    1,   # Corner 4
    1,   # Corner 5
    28,  # Corner 6  (High-speed DRS zone setup)
    1,   # Corner 7
    1,   # Corner 8  (Outlier suppression)
    1,   # Corner 9
    1,   # Corner 10 (Outlier suppression)
    1,   # Corner 11
    1,   # Corner 12
    1,   # Corner 13
    29,  # Corner 14 (Primary overtaking & heavy braking zone)
    1,   # Corner 15
    11,  # Corner 16 (Sector 3 chicane entry)
    30,  # Corner 17 (Critical mechanical traction exit)
    6,   # Corner 18 (Penultimate positioning corner)
    22   # Corner 19 (Final corner to Pit Straight)
], dtype=float)

A_matrix = np.outer(corner_scores, 1.0 / corner_scores)
eigenvalues, eigenvectors = np.linalg.eig(A_matrix)
max_idx = np.argmax(eigenvalues.real)
w_vector = np.abs(eigenvectors[:, max_idx].real)
w_vector = w_vector / np.sum(w_vector)

w_df = pd.DataFrame({
    'Corner': [f"Corner_{i}" for i in range(1, 20)],
    'AHP_Score': corner_scores.astype(int),
    'Weight_w': np.round(w_vector, 4)
})

w_df.to_csv('corner_weights_w.csv', index=False)
print(w_df.to_string(index=False))
print("\n-> บันทึกไฟล์ corner_weights_w.csv สำเร็จ!")