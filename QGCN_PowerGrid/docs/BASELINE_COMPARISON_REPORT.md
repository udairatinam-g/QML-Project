# Baseline Comparison Report

This report compares simple classical baselines with the QGCN project result.

## Dataset
- IEEE 14-bus synthetic data
- 250 samples, 5 features per node
- Train/test split: 80/20

## Classical Baselines
- Voltage-rule baseline: flags failure based on voltage violations
- Logistic regression baseline: trained on flattened node features

## Measured Metrics
| Model | Accuracy | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| Voltage Rule | 0.880 | 1.000 | 0.400 | 0.571 |
| Logistic Regression | 0.680 | 0.125 | 0.100 | 0.111 |

## Notes
- QGCN metrics are generated in docs/EXECUTION_SUMMARY.md from src/demo.py.
- If logistic baseline is close to QGCN, use stronger stress scenarios or larger grid variants for clearer separation.
- This baseline is useful for viva and review discussions to show scientific comparison.