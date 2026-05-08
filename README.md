# Quantum Graph Convolutional Networks for Power Grid Reliability

A hybrid quantum-classical approach for power grid failure prediction using Graph Convolutional Networks integrated with quantum circuits.

## Project Overview

This implementation combines:
- **Graph Convolutional Networks** for grid topology analysis
- **Quantum Circuits** for feature embedding and kernel methods
- **Hybrid Classical-Quantum Pipeline** for power grid risk prediction

## Project Structure

```
├── src/                               # Core implementation
│   ├── config.py                      # Configuration parameters
│   ├── phase1_data_modeling.py        # Power grid data simulation
│   ├── phase2_quantum_embedding.py    # Quantum feature embedding
│   ├── phase3_quantum_layer.py        # Quantum graph convolution
│   ├── phase4_training.py            # Model training and evaluation
│   ├── baseline_comparison.py         # Classical baseline comparison
│   ├── demo.py                        # Demonstration script
│   └── main.py                        # Full pipeline orchestration
│
├── notebooks/                         # Interactive development
│   ├── QGCN_quantum_demo.ipynb        # Quantum kernel demonstration
│   └── QGCN_Interactive_Notebook.ipynb # Full project notebook
│
├── requirements.txt                   # Project dependencies
└── README.md                          # This file
```

## Requirements

- Python 3.9+
- See `requirements.txt` for dependencies

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Project

### Quick Demo
```bash
python src/demo.py
```
Runs a quantum kernel demonstration with synthetic power grid data.

### Full Pipeline
```bash
python src/main.py
```
Executes the complete 4-phase pipeline:
- Phase 1: Grid data generation and preprocessing
- Phase 2: Quantum feature embedding
- Phase 3: Quantum graph convolutional layer
- Phase 4: Model training and evaluation

### Classical Baseline Comparison
```bash
python src/baseline_comparison.py
```
Compares quantum kernel methods against traditional ML baselines.

### Interactive Notebook
```bash
jupyter notebook notebooks/QGCN_quantum_demo.ipynb
```
Step-by-step quantum circuit construction and kernel analysis.

## Core Modules

### config.py
Configuration parameters for:
- Grid topology (nodes, edges)
- Quantum circuit parameters
- Training hyperparameters

### phase1_data_modeling.py
`PowerGridSimulator` class:
- Generates synthetic power grid data
- Constructs adjacency matrices
- Computes node features

### phase2_quantum_embedding.py
`GraphQuantumEmbedding` class:
- Angle-encoding for classical features
- Optional CNOT entanglement
- Statevector computation

### phase3_quantum_layer.py
`QuantumGraphConvolution` class:
- Quantum-based message passing
- Kernel computation for graph convolution
- Hybrid classical-quantum forward pass

### phase4_training.py
`QGCNModel` class:
- End-to-end training pipeline
- Binary classification on grid failures
- Model evaluation metrics

## Technical Details

The QGCN architecture leverages quantum kernel methods to capture complex relationships in power grid topology. The hybrid approach uses classical neural networks for feature extraction combined with quantum-enhanced kernel functions for improved generalization.
