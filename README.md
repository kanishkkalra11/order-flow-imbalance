# order-flow-imbalance

This project implements Order Flow Imbalance (OFI) feature creation from high-frequency limit order book (LOB) data. It follows the methodology described in the paper: Cross-impact of order flow imbalance in equity markets by Cont, Cucuringu, and Zhang (2023).

Features Computed:
- Best-Level OFI: Net order flow at the top of the book (depth 0).
- Multi-Level OFI: Depth-wise order flow imbalances from levels 0–9.
- Integrated OFI: A compressed 1D signal obtained via PCA on normalized multi-level OFIs.
All features are aggregated over non-overlapping 1-minute windows.

Usage:
```bash
python get_ofi.py
```
Input: See first_25000_rows.csv.
Output: ofi_features.csv containing OFI features per 1-minute interval. (See ofi_features.csv)

Dependencies:
See requirements.txt for necessary packages
