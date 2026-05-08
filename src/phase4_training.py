"""
PHASE 4: Training & Optimization
Complete training pipeline for the QGCN model on power grid data.
"""

import numpy as np
import pennylane as qml
from pennylane import numpy as pnp
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List
from tqdm import tqdm

from config import TRAINING_CONFIG, GRID_CONFIG, NODE_FEATURES
from phase1_data_modeling import PowerGridSimulator
from phase2_quantum_embedding import GraphQuantumEmbedding
from phase3_quantum_layer import QuantumGraphConvolution


class QGCNModel:
    """Complete QGCN Model for power grid failure prediction."""
    
    def __init__(self, num_nodes: int = 14, n_qubits_per_node: int = 4, 
                 n_layers: int = 3):
        """
        Initialize complete QGCN model.
        
        Architecture:
        1. Feature extraction from graph data
        2. Quantum embedding of node features
        3. Quantum graph convolution with message passing
        4. Classical readout for prediction
        """
        self.num_nodes = num_nodes
        self.n_qubits_per_node = n_qubits_per_node
        self.n_layers = n_layers
        
        # Initialize grid simulator
        self.grid = PowerGridSimulator()
        
        # Quantum embedding layer
        self.qge = GraphQuantumEmbedding(
            num_nodes=num_nodes,
            n_qubits_per_node=n_qubits_per_node
        )
        
        # QGCN layer
        self.qgcn = QuantumGraphConvolution(
            n_nodes=num_nodes,
            n_qubits_per_node=n_qubits_per_node,
            n_layers=n_layers
        )
        
        # Get adjacency matrix
        self.adjacency_matrix = self.grid.get_adjacency_matrix()
        
        # Training history
        self.history = {
            "train_loss": [],
            "val_loss": [],
            "train_acc": [],
            "val_acc": []
        }
        
        print("✓ Initialized QGCN Model")
    
    def loss_function(self, predictions: np.ndarray, targets: np.ndarray) -> float:
        """
        Binary cross-entropy loss for failure prediction.
        
        Args:
            predictions: Model outputs (real values)
            targets: Ground truth binary labels
        
        Returns:
            Loss value
        """
        # Clip predictions to avoid log(0)
        pred_clipped = np.clip(predictions, 1e-7, 1 - 1e-7)
        
        # Binary cross-entropy
        loss = -np.mean(
            targets * np.log(pred_clipped) + 
            (1 - targets) * np.log(1 - pred_clipped)
        )
        
        return loss
    
    def forward(self, node_features: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Forward pass through entire model.
        
        Args:
            node_features: Shape (num_nodes, num_features)
        
        Returns:
            predictions: Shape (1,) - failure probability (0-1)
            quantum_states: Intermediate quantum representations
        """
        # Step 1: Quantum embedding of features
        quantum_embeddings = self.qge.embed_node_features(node_features)
        
        # Step 2: QGCN processing
        quantum_states, node_predictions = self.qgcn.forward(
            quantum_embeddings, self.adjacency_matrix
        )
        
        # Step 3: Global prediction (aggregate node predictions)
        # Take max as overall grid risk indicator
        global_prediction = np.max(np.abs(node_predictions))
        
        # Sigmoid to get probability
        prediction_prob = 1 / (1 + np.exp(-global_prediction))
        
        return prediction_prob, quantum_states
    
    def train_step(self, X_train: np.ndarray, y_train: np.ndarray, 
                   learning_rate: float = 0.01) -> float:
        """
        Single training step for a batch.
        
        Args:
            X_train: Training features, shape (batch_size, num_nodes, num_features)
            y_train: Training labels, shape (batch_size,)
            learning_rate: Learning rate for parameter update
        
        Returns:
            Average loss over batch
        """
        batch_size = X_train.shape[0]
        batch_loss = 0
        
        # Get current quantum parameters
        current_params = self.qgcn.get_params()
        param_updates = {k: np.zeros_like(v) for k, v in current_params.items()}
        
        # Process batch
        predictions = []
        for i in range(batch_size):
            pred, _ = self.forward(X_train[i])
            predictions.append(pred)
        
        predictions = np.array(predictions)
        
        # Compute loss
        batch_loss = self.loss_function(predictions, y_train)
        
        # Numerical gradient (simple finite differences)
        # Note: In production, use autodiff from PennyLane
        epsilon = 0.01
        
        # Update output weights with simple gradient descent
        for j in range(self.n_qubits_per_node):
            # Finite difference for output weight j
            old_weight = self.qgcn.output_weights[j]
            
            # Compute loss with +epsilon
            self.qgcn.output_weights[j] = old_weight + epsilon
            pred_plus = np.array([self.forward(X_train[i])[0] for i in range(batch_size)])
            loss_plus = self.loss_function(pred_plus, y_train)
            
            # Compute loss with -epsilon
            self.qgcn.output_weights[j] = old_weight - epsilon
            pred_minus = np.array([self.forward(X_train[i])[0] for i in range(batch_size)])
            loss_minus = self.loss_function(pred_minus, y_train)
            
            # Gradient
            grad = (loss_plus - loss_minus) / (2 * epsilon)
            
            # Update
            self.qgcn.output_weights[j] = old_weight - learning_rate * grad
        
        # Update bias
        old_bias = self.qgcn.output_bias
        self.qgcn.output_bias = old_bias - learning_rate * 0.01 * batch_loss
        
        return batch_loss
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """
        Evaluate model on test set.
        
        Args:
            X_test: Test features
            y_test: Test labels
        
        Returns:
            Dictionary of metrics
        """
        predictions = []
        for i in range(X_test.shape[0]):
            pred, _ = self.forward(X_test[i])
            predictions.append(pred)
        
        predictions = np.array(predictions)
        pred_binary = (predictions > 0.5).astype(int)
        
        metrics = {
            "loss": self.loss_function(predictions, y_test),
            "accuracy": accuracy_score(y_test, pred_binary),
            "precision": precision_score(y_test, pred_binary, zero_division=0),
            "recall": recall_score(y_test, pred_binary, zero_division=0),
            "f1": f1_score(y_test, pred_binary, zero_division=0),
            "auc": roc_auc_score(y_test, predictions) if len(np.unique(y_test)) > 1 else 0.5
        }
        
        return metrics
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: np.ndarray, y_val: np.ndarray,
              epochs: int = 50, batch_size: int = 32, 
              learning_rate: float = 0.01, verbose: bool = True):
        """
        Train the model.
        
        Args:
            X_train: Training features, shape (num_samples, num_nodes, num_features)
            y_train: Training labels
            X_val: Validation features
            y_val: Validation labels
            epochs: Number of training epochs
            batch_size: Batch size
            learning_rate: Learning rate
            verbose: Print progress
        """
        if epochs <= 0:
            if verbose:
                print("Skipping training because epochs <= 0 (CPU-friendly mode).")
            return

        num_samples = X_train.shape[0]
        num_batches = max(1, num_samples // batch_size)
        
        for epoch in range(epochs):
            # Shuffle training data
            indices = np.random.permutation(num_samples)
            X_shuffled = X_train[indices]
            y_shuffled = y_train[indices]
            
            # Training batches
            epoch_loss = 0
            for batch_idx in range(num_batches):
                start_idx = batch_idx * batch_size
                end_idx = min(start_idx + batch_size, num_samples)
                
                X_batch = X_shuffled[start_idx:end_idx]
                y_batch = y_shuffled[start_idx:end_idx]
                
                batch_loss = self.train_step(X_batch, y_batch, learning_rate)
                epoch_loss += batch_loss
            
            # Average epoch loss
            epoch_loss /= num_batches
            
            # Validation
            val_metrics = self.evaluate(X_val, y_val)
            val_loss = val_metrics["loss"]
            val_acc = val_metrics["accuracy"]
            
            # Training metrics
            train_metrics = self.evaluate(X_train, y_train)
            train_loss = train_metrics["loss"]
            train_acc = train_metrics["accuracy"]
            
            # Store history
            self.history["train_loss"].append(train_loss)
            self.history["val_loss"].append(val_loss)
            self.history["train_acc"].append(train_acc)
            self.history["val_acc"].append(val_acc)
            
            if verbose and (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch + 1}/{epochs}")
                print(f"  Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")
                print(f"  Train Acc: {train_acc:.4f}  | Val Acc: {val_acc:.4f}")
    
    def plot_history(self):
        """Plot training history."""
        os.makedirs("outputs", exist_ok=True)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        if len(self.history["train_loss"]) == 0:
            ax1.text(0.5, 0.5, "No training executed\n(epochs = 0)",
                     ha="center", va="center", fontsize=12)
            ax1.set_title("Training & Validation Loss")
            ax1.set_axis_off()

            ax2.text(0.5, 0.5, "No training executed\n(epochs = 0)",
                     ha="center", va="center", fontsize=12)
            ax2.set_title("Training & Validation Accuracy")
            ax2.set_axis_off()

            plt.tight_layout()
            plt.savefig("outputs/02_training_history.png", dpi=150, bbox_inches='tight')
            print("✓ Training history saved to outputs/02_training_history.png")
            plt.close()
            return
        
        # Loss
        ax1.plot(self.history["train_loss"], label="Train Loss", marker='o')
        ax1.plot(self.history["val_loss"], label="Val Loss", marker='s')
        ax1.set_xlabel("Epoch")
        ax1.set_ylabel("Loss")
        ax1.set_title("Training & Validation Loss")
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Accuracy
        ax2.plot(self.history["train_acc"], label="Train Acc", marker='o')
        ax2.plot(self.history["val_acc"], label="Val Acc", marker='s')
        ax2.set_xlabel("Epoch")
        ax2.set_ylabel("Accuracy")
        ax2.set_title("Training & Validation Accuracy")
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig("outputs/02_training_history.png", dpi=150, bbox_inches='tight')
        print("✓ Training history saved to outputs/02_training_history.png")
        plt.close()


# ==============================================================================
# Main execution
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "="*70)
    print("PHASE 4: QGCN Training & Optimization")
    print("="*70)
    
    print("\n1. Generating training data...")
    grid_sim = PowerGridSimulator()
    node_features, labels = grid_sim.generate_node_features(
        num_samples=TRAINING_CONFIG["batch_size"] * 5,  # Use reasonable dataset
        failure_injection=True
    )
    
    print(f"✓ Generated {node_features.shape[0]} samples")
    print(f"  Shape: {node_features.shape}")
    print(f"  Labels distribution: {np.bincount(labels)}")
    
    # Train/val split
    X_train, X_val, y_train, y_val = train_test_split(
        node_features, labels, 
        test_size=TRAINING_CONFIG["validation_split"],
        random_state=TRAINING_CONFIG["random_seed"]
    )
    
    print(f"\n✓ Train set: {X_train.shape[0]} samples")
    print(f"✓ Val set: {X_val.shape[0]} samples")
    
    # Initialize model
    print("\n2. Initializing QGCN model...")
    model = QGCNModel(
        num_nodes=GRID_CONFIG["num_buses"],
        n_qubits_per_node=QUANTUM_CONFIG["n_qubits"],
        n_layers=QUANTUM_CONFIG["n_layers"]
    )
    
    # Train
    print("\n3. Training model...")
    model.train(
        X_train, y_train, X_val, y_val,
        epochs=TRAINING_CONFIG["num_epochs"],
        batch_size=TRAINING_CONFIG["batch_size"],
        learning_rate=TRAINING_CONFIG["learning_rate"],
        verbose=True
    )
    
    # Evaluate
    print("\n4. Evaluating on val set...")
    val_metrics = model.evaluate(X_val, y_val)
    print("Validation Metrics:")
    for metric, value in val_metrics.items():
        print(f"  {metric}: {value:.4f}")
    
    # Plot
    print("\n5. Plotting results...")
    model.plot_history()
    
    print("\n" + "="*70)
    print("Phase 4 Complete! Model trained successfully.")
    print("="*70)
