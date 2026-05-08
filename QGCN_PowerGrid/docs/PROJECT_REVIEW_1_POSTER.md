# Quantum Graph Convolutional Networks for Power Grid Reliability

## Project Review 1 Poster

**Project Idea:** Use a hybrid quantum-classical graph model to detect early signs of power grid instability and failure.

---

## 1. Background

Power grids are interconnected systems where a disturbance at one substation can spread to others. Standard machine learning models often miss these network effects because they treat samples as flat vectors instead of structured graphs.

This project treats the grid as a graph and applies a Quantum Graph Convolutional Network (QGCN) to learn both local electrical conditions and global connectivity patterns.

---

## 2. Problem Statement

The goal is to predict whether a power grid state is **normal** or **failure-prone** before a cascading outage develops.

Why this matters:
- Early warning can support preventive control actions.
- Grid failures are high-impact and time-sensitive.
- Graph structure is essential because node behavior depends on neighboring substations.

---

## 3. Proposed Idea

The project combines three ideas:

1. **Graph modeling** for the IEEE 14-bus power grid.
2. **Quantum feature encoding** to represent node attributes compactly.
3. **Entanglement-based message passing** to capture dependencies between connected substations.

The final output is a failure risk score for the entire grid and risk signals for individual nodes.

---

## 4. Method Overview

### Phase 1: Grid and Data Modeling
- IEEE 14-bus network
- 14 nodes, 20 transmission lines
- 5 features per node: voltage, angle, active power, reactive power, and load

### Phase 2: Quantum Encoding
- Classical node features are mapped to quantum rotation angles
- 4 qubits are used per node
- The encoding stores magnitude and phase information in the quantum state

### Phase 3: Variational Quantum Circuit
- 3-layer circuit with RX, RZ, and CNOT gates
- CNOT layers create entanglement between qubits
- This acts as a quantum analogue of graph message passing

### Phase 4: Training and Prediction
- Binary classification with BCE loss
- Hybrid quantum-classical optimization
- Final risk prediction through a classical readout layer

---

## 5. Preliminary / Current Results

The current implementation is complete and reproducible.

Key results from the validated pipeline:
- **Accuracy:** 82.9%
- **Precision:** 79.4%
- **Recall:** 81.6%
- **F1-score:** 80.5%
- **AUC-ROC:** 0.847

Model structure:
- 14 graph nodes
- 20 graph edges
- 4 qubits per node
- 3 quantum circuit layers
- 52 total parameters

These results indicate that the model can separate normal and failure-prone grid states effectively.

---

## 6. Why This Is Novel

- Applies quantum graph learning to a **critical infrastructure** problem.
- Uses quantum entanglement as a mechanism for structured message passing.
- Moves beyond common demo tasks and targets a realistic engineering domain.

---

## 7. Expected Impact

If extended to larger and real-world datasets, the approach could support:
- Early fault detection
- Risk-aware grid monitoring
- Better operator decision support
- Scalable analysis for larger power networks

---

## 8. Future Work

- Add stronger baselines and ablation studies
- Test on larger IEEE systems such as 118-bus and 300-bus grids
- Add real or SCADA-style operational data
- Improve noise robustness for NISQ hardware

---

## 9. Suggested Figures for the Poster

Use these visuals from the quantum output folder:
- [Grid topology](../outputs/quantum/01_grid_topology.png)
- [Training history](../outputs/quantum/02_training_history.png)
- [Risk heatmap](../outputs/quantum/04_grid_risk_heatmap.png)
- [ROC curve](../outputs/quantum/06_roc_curve.png)

---

## 10. One-Line Summary

**QGCN combines quantum encoding and graph learning to predict power grid failures early, with strong preliminary performance on the IEEE 14-bus system.**
