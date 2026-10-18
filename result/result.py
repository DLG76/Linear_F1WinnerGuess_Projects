import numpy as np
import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import TARGET_YEAR

p_file = f'performance_matrix_P_{TARGET_YEAR}.csv'
P_df = pd.read_csv(p_file, index_col=0)
w_df = pd.read_csv('corner_weights_w.csv')

drivers = P_df.columns.tolist()
P_matrix = P_df.values
w_vector = w_df['Weight_w'].values
w_vector = w_vector / np.sum(w_vector)

s_base = np.dot(P_matrix.T, w_vector)

rank_df = pd.DataFrame({
    'Driver': drivers,
    'Base_Score': np.round(s_base, 4)
}).sort_values(by='Base_Score', ascending=False).reset_index(drop=True)
rank_df['Initial_Rank'] = rank_df.index + 1

T_matrix = np.array([
    [0.80, 0.10, 0.05, 0.02, 0.01, 0.01, 0.01],
    [0.10, 0.50, 0.15, 0.05, 0.05, 0.05, 0.10],
    [0.05, 0.15, 0.60, 0.10, 0.05, 0.03, 0.02],
    [0.02, 0.05, 0.10, 0.55, 0.15, 0.08, 0.05],
    [0.01, 0.05, 0.05, 0.18, 0.55, 0.10, 0.06],
    [0.01, 0.10, 0.03, 0.05, 0.14, 0.60, 0.07],
    [0.01, 0.05, 0.02, 0.05, 0.05, 0.13, 0.69]
])

n_sc = 1
T_power_n = np.linalg.matrix_power(T_matrix, n_sc)
rank_df['Post_SC_Score'] = np.round(np.dot(T_power_n, rank_df['Base_Score'].values), 4)

def softmax(x, beta=5.0):
    scaled_x = beta * (x - np.max(x))
    exp_x = np.exp(scaled_x)
    return exp_x / np.sum(exp_x)

rank_df['Win_Prob_No_SC (%)'] = np.round(softmax(rank_df['Base_Score'].values, beta=5.0) * 100, 2)
rank_df['Win_Prob_With_SC (%)'] = np.round(softmax(rank_df['Post_SC_Score'].values, beta=5.0) * 100, 2)

final_results = rank_df.sort_values(by='Win_Prob_With_SC (%)', ascending=False).reset_index(drop=True)
final_results['Final_Rank'] = final_results.index + 1

cols_to_show = ['Final_Rank', 'Driver', 'Base_Score', 'Post_SC_Score', 'Win_Prob_No_SC (%)', 'Win_Prob_With_SC (%)']
print(f"\n=== result winrate Singapore GP {TARGET_YEAR} ===")
print(final_results[cols_to_show].to_string(index=False))

out_file = f'final_race_prediction_{TARGET_YEAR}.csv'
final_results[cols_to_show].to_csv(out_file, index=False)
print(f"\n-> save {out_file} success")