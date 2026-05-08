"""
QGCN for Power Grid Reliability: Complete Pipeline
Main orchestration script that runs all phases.
"""

import sys
import numpy as np
from sklearn.model_selection import train_test_split

from config import TRAINING_CONFIG, GRID_CONFIG, QUANTUM_CONFIG, NODE_FEATURES
from phase1_data_modeling import PowerGridSimulator
from phase2_quantum_embedding import GraphQuantumEmbedding
from phase3_quantum_layer import QuantumGraphConvolution
from phase4_training import QGCNModel


def print_header(title: str):
    """Print formatted header."""
    print("\n" + "="*80)
    print(" " * ((80 - len(title)) // 2) + title)
    print("="*80)


def main():
    """Run complete QGCN pipeline."""
    
    print_header("QUANTUM GRAPH CONVOLUTIONAL NETWORK")
    print("POWER GRID FAILURE PREDICTION & OPTIMIZATION")
    
    # ===========================================================================
    # PHASE 1: Data Modeling
    # ===========================================================================
    print_header("PHASE 1: Power Grid Data Modeling")
    
    print("\n[1.1] Creating IEEE 14-Bus Power Grid...")
    grid_simulator = PowerGridSimulator(config=GRID_CONFIG)
    
    print("\n[1.2] Grid Statistics:")
    grid_info = grid_simulator.get_graph_info()
    for key, value in grid_info.items():
        print(f"  {key:.<30} {value}")
    
    print("\n[1.3] Generating Synthetic Operational Data...")
    node_features, failure_labels = grid_simulator.generate_node_features(
        num_samples=TRAINING_CONFIG["batch_size"] * 8,
        failure_injection=True
    )
    
    print(f"  Generated: {node_features.shape[0]} samples")
    print(f"  Features per node: {node_features.shape[2]}")
    print(f"  Samples with failures: {np.sum(failure_labels == 1)}")
    print(f"  Failure rate: {np.mean(failure_labels):.2%}")
    
    print("\n[1.4] Visualizing Grid Topology...")
    grid_simulator.visualize_grid(save_path="outputs/01_power_grid_topology.png")
    
    # ===========================================================================
    # PHASE 2: Quantum Embedding
    # ===========================================================================
    print_header("PHASE 2: Quantum Feature Encoding")
    
    print(f"\n[2.1] Initializing Quantum Feature Encoder...")
    qge = GraphQuantumEmbedding(
        num_nodes=GRID_CONFIG["num_buses"],
        n_qubits_per_node=QUANTUM_CONFIG["n_qubits"],
        encoding_method=QUANTUM_CONFIG["encoding_method"]
    )
    
    print(f"\n[2.2] Encoding Features into Quantum States...")
    print(f"  Encoding method: {QUANTUM_CONFIG['encoding_method']}")
    print(f"  Qubits per node: {QUANTUM_CONFIG['n_qubits']}")
    
    # Embed a sample
    sample_idx = 0
    quantum_embeddings_sample = qge.embed_node_features(node_features[sample_idx])
    
    print(f"\n[2.3] Quantum Embeddings (sample):")
    print(f"  Shape: {quantum_embeddings_sample.shape}")
    print(f"  First node quantum state: {quantum_embeddings_sample[0]}")
    print(f"  Quantum state values range: [{quantum_embeddings_sample.min():.4f}, "
          f"{quantum_embeddings_sample.max():.4f}]")
    
    # ===========================================================================
    # PHASE 3: Quantum Graph Convolution
    # ===========================================================================
    print_header("PHASE 3: Quantum Graph Convolution")
    
    print(f"\n[3.1] Building Variational Quantum Circuit...")
    qgcn = QuantumGraphConvolution(
        n_nodes=GRID_CONFIG["num_buses"],
        n_qubits_per_node=QUANTUM_CONFIG["n_qubits"],
        n_layers=QUANTUM_CONFIG["n_layers"]
    )
    
    params = qgcn.get_params()
    total_params = (params['quantum_params'].size + 
                   params['output_weights'].size + 1)
    
    print(f"  VQC Depth: {QUANTUM_CONFIG['n_layers']} layers")
    print(f"  Total Trainable Parameters: {total_params}")
    
    print(f"\n[3.2] Testing Message Passing on Sample Graph...")
    adj_matrix = grid_simulator.get_adjacency_matrix()
    quantum_states, predictions = qgcn.forward(quantum_embeddings_sample, adj_matrix)
    
    print(f"  Input quantum embeddings: {quantum_embeddings_sample.shape}")
    print(f"  Output quantum states: {quantum_states.shape}")
    print(f"  Node predictions: {predictions.shape}")
    print(f"  Prediction range: [{predictions.min():.4f}, {predictions.max():.4f}]")
    
    # ===========================================================================
    # PHASE 4: Training & Optimization
    # ===========================================================================
    print_header("PHASE 4: Model Training")
    
    print(f"\n[4.1] Preparing Training Data...")
    X_train, X_val, y_train, y_val = train_test_split(
        node_features, failure_labels,
        test_size=TRAINING_CONFIG["validation_split"],
        random_state=TRAINING_CONFIG["random_seed"]
    )
    
    print(f"  Training samples: {X_train.shape[0]}")
    print(f"  Validation samples: {X_val.shape[0]}")
    print(f"  Training failure rate: {np.mean(y_train):.2%}")
    print(f"  Validation failure rate: {np.mean(y_val):.2%}")
    
    print(f"\n[4.2] Initializing QGCN Model...")
    model = QGCNModel(
        num_nodes=GRID_CONFIG["num_buses"],
        n_qubits_per_node=QUANTUM_CONFIG["n_qubits"],
        n_layers=QUANTUM_CONFIG["n_layers"]
    )
    
    print(f"\n[4.3] Training Model ({TRAINING_CONFIG['num_epochs']} epochs)...")
    if TRAINING_CONFIG["num_epochs"] > 0:
        model.train(
            X_train, y_train, X_val, y_val,
            epochs=TRAINING_CONFIG["num_epochs"],
            batch_size=TRAINING_CONFIG["batch_size"],
            learning_rate=TRAINING_CONFIG["learning_rate"],
            verbose=True
        )
    else:
        print("  Skipping training because num_epochs is set to 0 (CPU-friendly mode).")
    
    print(f"\n[4.4] Final Validation Metrics...")
    final_metrics = model.evaluate(X_val, y_val)
    
    print("  Metric               Value")
    print("  " + "-"*35)
    for metric, value in final_metrics.items():
        print(f"  {metric:.<20} {value:.4f}")
    
    # ===========================================================================
    # Results & Visualization
    # ===========================================================================
    print_header("RESULTS & ANALYSIS")
    
    print(f"\n[5.1] Training Convergence...")
    if len(model.history["val_acc"]) > 0:
        best_val_acc = max(model.history["val_acc"])
        best_epoch = model.history["val_acc"].index(best_val_acc) + 1
        print(f"  Best validation accuracy: {best_val_acc:.4f} at epoch {best_epoch}")
    else:
        print("  Training was skipped (0 epochs), so convergence metrics are not available.")
    
    print(f"\n[5.2] Generating Visualizations...")
    model.plot_history()
    print("  ✓ Training history saved to outputs/02_training_history.png")
    
    # ===========================================================================
    # Summary
    # ===========================================================================
    print_header("PROJECT SUMMARY")
    
    print(f"""
    ✓ QGCN Architecture Successfully Built for Power Grid Analysis
    
    ARCHITECTURE LAYERS:
    ────────────────────────────────────────────────────────────────
    1. Data Layer:        IEEE 14-bus power grid (14 nodes, 20 edges)
    2. Feature Layer:     5 features per node (voltage, power, load)
    3. Quantum Layer:     {QUANTUM_CONFIG['n_qubits']} qubits × {GRID_CONFIG['num_buses']} nodes
    4. VQC Layer:         {QUANTUM_CONFIG['n_layers']} variational circuit layers
    5. Message Passing:   Quantum state fusion with neighbor info
    6. Readout Layer:     Classical output mapping ({total_params} params)
    
    PERFORMANCE:
    ────────────────────────────────────────────────────────────────
    Final Accuracy:       {final_metrics['accuracy']:.4f}
    Final Precision:      {final_metrics['precision']:.4f}
    Final Recall:         {final_metrics['recall']:.4f}
    Final F1-Score:       {final_metrics['f1']:.4f}
    Final AUC:            {final_metrics['auc']:.4f}
    
    KEY ADVANTAGES:
    ────────────────────────────────────────────────────────────────
    • Quantum advantage: Entanglement captures graph correlations
    • Scalability: Modular design for larger grids
    • Inference: Fast quantum simulation (no noise)
    • Interpretability: Each node's quantum state is trackable
    
    FILES GENERATED:
    ────────────────────────────────────────────────────────────────
    • power_grid_topology.png      - Grid visualization
    • outputs/02_training_history.png - Loss & accuracy curves
    • *.py modules                  - Reusable components
    """)
    
    print_header("PROJECT COMPLETE")
    print("\n✓ All phases executed successfully!")
    print("✓ Next steps: Fine-tune hyperparameters, test on real data,")
    print("  or scale to larger power grids (IEEE 118-bus, 300-bus systems)")
    print("\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error during execution: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
