# Imports
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

def load_and_filter_data(filepath, levels):
    df = pd.read_csv(filepath, parse_dates=["ts_event"]) # Load the dataset
    lob_columns = [f"{side}_{attr}_{str(i).zfill(2)}"
                   for attr in ['px', 'sz', 'ct']
                   for side in ['bid', 'ask']
                   for i in levels]
    lob_diff = df[lob_columns].diff().abs().sum(axis=1)
    change_mask = lob_diff > 0
    change_mask.iloc[0] = True
    return df[change_mask].reset_index(drop=True) # Remove useless events that don't affect the order book

def compute_order_flow(df, levels):
    of_bid, of_ask = [], []
    for m in levels:
        px_b, sz_b = df[f"bid_px_{str(m).zfill(2)}"].values, df[f"bid_sz_{str(m).zfill(2)}"].values
        px_a, sz_a = df[f"ask_px_{str(m).zfill(2)}"].values, df[f"ask_sz_{str(m).zfill(2)}"].values
        px_b_prev, sz_b_prev = np.roll(px_b, 1), np.roll(sz_b, 1)
        px_a_prev, sz_a_prev = np.roll(px_a, 1), np.roll(sz_a, 1)

        of_b = np.where(px_b > px_b_prev, sz_b,
               np.where(px_b == px_b_prev, sz_b - sz_b_prev, -sz_b))
        of_a = np.where(px_a > px_a_prev, -sz_a,
               np.where(px_a == px_a_prev, sz_a - sz_a_prev, sz_a))
        of_b[0], of_a[0] = 0, 0  # Invalidate first row

        of_bid.append(of_b)
        of_ask.append(of_a)
    return np.stack(of_bid, axis=1), np.stack(of_ask, axis=1)

def aggregate_ofi(df, ofi_per_level, levels):
    df["minute"] = df["ts_event"].dt.floor("1min") # Assign each row to a 1-minute bin
    ofi_df = pd.DataFrame(ofi_per_level, columns=[f"OFI_{m}" for m in levels])
    ofi_df["minute"] = df["minute"]
    return ofi_df.groupby("minute").sum() # Aggregate OFIs into 1-minute intervals

def compute_normalization(df, levels):
    q_m_vals = [((df[f"bid_sz_{str(m).zfill(2)}"] + df[f"ask_sz_{str(m).zfill(2)}"]) / 2) for m in levels]
    q_matrix = pd.concat(q_m_vals, axis=1)
    q_matrix["minute"] = df["minute"]
    return q_matrix.groupby("minute").mean().mean(axis=1) # Compute normalization term Q_M for each minute

def normalize_ofi(ofi_agg, Q_M, levels):
    normalized = ofi_agg[[f"OFI_{m}" for m in levels]].div(Q_M, axis=0) # Normalize multi-level OFIs
    normalized['Best_level_OFI'] = normalized["OFI_0"]
    return normalized

def compute_integrated_ofi(normalized_ofis, levels):
    pca = PCA(n_components=1) # PCA for Integrated OFI
    pca.fit(normalized_ofis[[f"OFI_{m}" for m in levels]].fillna(0))
    weights = pca.components_[0]
    w1_l1 = np.sum(np.abs(weights))
    integrated_ofi = np.dot(normalized_ofis[[f"OFI_{m}" for m in levels]], weights.T) / w1_l1
    return integrated_ofi

def main(filepath, output_csv="ofi_features.csv"):
    levels = list(range(10))
    df = load_and_filter_data(filepath, levels)
    of_bid, of_ask = compute_order_flow(df, levels)
    ofi_per_level = of_bid - of_ask
    ofi_agg = aggregate_ofi(df, ofi_per_level, levels)
    Q_M = compute_normalization(df, levels)
    normalized_ofis = normalize_ofi(ofi_agg, Q_M, levels)
    normalized_ofis["Integrated_OFI"] = compute_integrated_ofi(normalized_ofis, levels)
    ofi_features = normalized_ofis[["Best_level_OFI", "Integrated_OFI"] + [f"OFI_{m}" for m in levels]]
    ofi_features.to_csv(output_csv)
    return ofi_features

# Execute the pipeline
ofi_features = main("first_25000_rows.csv")
print(ofi_features.to_string())

