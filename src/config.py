"""
Configuration for QGCN Power Grid Optimization Project
"""

# ============================================================================
# GRID CONFIGURATION - IEEE 14-Bus System
# ============================================================================
GRID_CONFIG = {
    "num_buses": 14,
    "num_generators": 5,  # Generator buses
    "num_transmission_lines": 20,
    "nominal_voltage": 1.0,  # per unit
    "base_power": 100,  # MVA
}

# ============================================================================
# NODE FEATURE CONFIGURATION
# ============================================================================
NODE_FEATURES = {
    "voltage_magnitude": {"min": 0.9, "max": 1.1},
    "voltage_angle": {"min": -0.5, "max": 0.5},  # radians
    "active_power": {"min": -2.0, "max": 2.0},  # per unit
    "reactive_power": {"min": -1.0, "max": 1.0},  # per unit
    "load_level": {"min": 0.0, "max": 1.0},  # load variation
}

# ============================================================================
# QUANTUM CIRCUIT CONFIGURATION
# ============================================================================
QUANTUM_CONFIG = {
    "n_qubits": 4,  # Number of qubits per node
    "n_layers": 3,  # Depth of quantum circuit
    "encoding_method": "angle",  # "angle", "amplitude", or "iqp"
    "entanglement_gate": "CNOT",
    "measurement_basis": "Z",
}

# ============================================================================
# TRAINING CONFIGURATION
# ============================================================================
TRAINING_CONFIG = {
    "batch_size": 32,
    "learning_rate": 0.01,
    "num_epochs": 0,
    "optimizer": "adam",
    "loss_function": "mse",  # Mean Squared Error
    "validation_split": 0.2,
    "random_seed": 42,
}

# ============================================================================
# MODEL ARCHITECTURE
# ============================================================================
MODEL_CONFIG = {
    "input_dim": len(NODE_FEATURES),  # Number of node features
    "hidden_dim": 16,
    "output_dim": 1,  # Binary classification: Normal (0) or Failure (1)
    "task": "failure_prediction",  # "failure_prediction" or "optimization"
}

# ============================================================================
# DATA SIMULATION PARAMETERS
# ============================================================================
DATA_CONFIG = {
    "num_samples": 500,  # Number of synthetic samples
    "noise_level": 0.05,  # Gaussian noise std
    "failure_probability": 0.15,  # Probability of grid failure
    "test_size": 0.2,
}

# ============================================================================
# MONITORING & LOGGING
# ============================================================================
LOGGING_CONFIG = {
    "log_file": "qgcn_training.log",
    "log_level": "INFO",
    "plot_results": True,
    "save_model": True,
    "model_checkpoint_dir": "checkpoints",
}
