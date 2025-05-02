# order-flow-imbalance

This project implements Order Flow Imbalance (OFI) feature creation from high-frequency limit order book (LOB) data. It follows the methodology described in the paper: Cross-impact of order flow imbalance in equity markets by Cont, Cucuringu, and Zhang (2023).

Features Computed:
- Best-Level OFI: Net order flow at the top of the book (depth 0).
- Multi-Level OFI: Depth-wise order flow imbalances from levels 0–9.
- Integrated OFI: A compressed 1D signal obtained via PCA on normalized multi-level OFIs.<br>

All features are aggregated over non-overlapping 1-minute windows.<br>
<b>Note:</b> Cross-Asset OFI can not be calculated here as there is only one instrument in this dataset.

<b>Usage:</b>
```bash
python get_ofi.py
```
Input: See first_25000_rows.csv.<br>
Output: ofi_features.csv containing OFI features per 1-minute interval. (See ofi_features.csv)
Dependencies: See requirements.txt for necessary packages

<h3>Data Exploration and Assumptions</h3>

Here are some key observations, potential data inconsistencies, assumptions, and cleaning decisions for this task:

* There are gaps in sequence numbers. These gaps were assumed non-informative and do not compromise OFI computation. However, a few inconsistencies in the data were observed as given below
* Book state inconsistencies examples: At index 7 - A new order at book level 1 should push down the other levels, however, the price at level 2 was removed instead of appearing at level 3; At index 267 - a new best bid level was added whose event is not available in the data; At index 962 - the new event adds a new buy order at depth 0 but the new price is lower than the already present best bid. There are multiple examples of this in the dataset. These have been ignored for the purposes of this task.
* Action T (Trade) likely indicates IOC orders. Side N probably indicates the order did not reach the book (e.g., rejected or expired).
* When a trade event is successful, it sometimes (mostly in cases where the entire order is fulfilled) appears as two different rows having the same sequence number, the second row being cancel event to remove the traded volume.
* There are three instances of 'Add' event on 'N' side which behave like 'Add' event on 'Ask' side. Calculations are done using this assumption.
* Removed events with no visible order book change, defined as events where no price or size value changed across any of the top 10 bid or ask levels. This is based on the rationale that they do not affect liquidity pressure and removing them improves both computational efficiency and signal clarity.

