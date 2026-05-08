"""
PHASE 2: Quantum Embedding
Encodes node features into quantum states using various encoding schemes.
"""

import numpy as np
import pennylane as qml
from pennylane import numpy as pnp
from typing import Callable, List
from config import QUANTUM_CONFIG, NODE_FEATURES


class QuantumFeatureEncoder:
    """Encodes classical features into quantum states."""
    
    def __init__(self, n_qubits: int = 4, encoding_method: str = "angle"):
        """
        Initialize quantum encoder.
        
        Args:
            n_qubits: Number of qubits
            encoding_method: "angle", "amplitude", or "iqp"
        """
        self.n_qubits = n_qubits
        self.encoding_method = encoding_method
        
        # Use default.qubit for statevector simulation
        self.dev = qml.device('default.qubit', wires=n_qubits)
        
        print(f"✓ Initialized Quantum Feature Encoder")
        print(f"  - Qubits: {n_qubits}")
        print(f"  - Encoding: {encoding_method}")
    
    def angle_encoding(self, features: np.ndarray) -> np.ndarray:
        """
        Angle Encoding: Map feature values to rotation angles.
        Each qubit rotates by an angle proportional to a feature.
        
        Formula: |ψ⟩ = ⊗_i RZ(feature_i) |0⟩
        """
        @qml.qnode(self.dev)
        def encoded_circuit(x):
            # Normalize features to [-π, π]
            x_normalized = np.clip(x, -1, 1) * np.pi
            
            # Use non-commuting rotations so Z-basis measurements carry feature signal.
            for i in range(self.n_qubits):
                theta = x_normalized[i % len(x_normalized)]
                phi = x_normalized[(i + 1) % len(x_normalized)] if len(x_normalized) > 1 else theta
                qml.RX(theta, wires=i)
                qml.RY(phi, wires=i)

            if self.n_qubits > 1:
                for i in range(self.n_qubits - 1):
                    qml.CNOT(wires=[i, i + 1])
            
            # Apply X-basis measurement for feature extraction
            return [qml.expval(qml.PauliZ(i)) for i in range(self.n_qubits)]
        
        return np.array(encoded_circuit(features))
    
    def amplitude_encoding(self, features: np.ndarray) -> np.ndarray:
        """
        Amplitude Encoding: Normalize features and use as amplitudes.
        Requires exactly 2^n_qubits features.
        """
        # Pad or truncate to 2^n_qubits
        n_amplitudes = 2 ** self.n_qubits
        
        if len(features) < n_amplitudes:
            features_padded = np.pad(features, (0, n_amplitudes - len(features)))
        else:
            features_padded = features[:n_amplitudes]
        
        # Normalize
        norm = np.linalg.norm(features_padded)
        if norm > 0:
            features_normalized = features_padded / norm
        else:
            features_normalized = features_padded
        
        @qml.qnode(self.dev)
        def amplitude_circuit(x):
            # State preparation using arbitrary unitary
            qml.StatePrep(x, wires=range(self.n_qubits))
            return [qml.expval(qml.PauliZ(i)) for i in range(self.n_qubits)]
        
        return np.array(amplitude_circuit(features_normalized))
    
    def iqp_encoding(self, features: np.ndarray) -> np.ndarray:
        """
        IQP (Instantaneous Quantum Polynomial) Encoding.
        Uses U3 gates with feature-dependent interactions.
        """
        @qml.qnode(self.dev)
        def iqp_circuit(x):
            # Normalize features
            x_norm = np.clip(x, -1, 1) * np.pi
            
            # Single qubit rotations
            for i in range(min(len(x_norm), self.n_qubits)):
                qml.RZ(x_norm[i], wires=i)
                qml.RX(x_norm[i] / 2, wires=i)
            
            # Two-qubit interactions (IQP structure)
            for i in range(self.n_qubits - 1):
                for j in range(i + 1, self.n_qubits):
                    param = x_norm[i % len(x_norm)] * x_norm[j % len(x_norm)]
                    qml.CNOT(wires=[i, j])
                    qml.RZ(param, wires=j)
                    qml.CNOT(wires=[i, j])
            
            return [qml.expval(qml.PauliZ(i)) for i in range(self.n_qubits)]
        
        return np.array(iqp_circuit(features))
    
    def encode(self, features: np.ndarray) -> np.ndarray:
        """
        Encode features using the selected encoding method.
        
        Args:
            features: Array of features, shape (num_features,)
        
        Returns:
            Quantum expectation values, shape (n_qubits,)
        """
        if self.encoding_method == "angle":
            return self.angle_encoding(features)
        elif self.encoding_method == "amplitude":
            return self.amplitude_encoding(features)
        elif self.encoding_method == "iqp":
            return self.iqp_encoding(features)
        else:
            raise ValueError(f"Unknown encoding method: {self.encoding_method}")
    
    def encode_batch(self, features_batch: np.ndarray) -> np.ndarray:
        """
        Encode a batch of features.
        
        Args:
            features_batch: Shape (batch_size, num_features)
        
        Returns:
            Quantum embeddings, shape (batch_size, n_qubits)
        """
        batch_size = features_batch.shape[0]
        embeddings = np.zeros((batch_size, self.n_qubits))
        
        for i in range(batch_size):
            embeddings[i] = self.encode(features_batch[i])
        
        return embeddings


class GraphQuantumEmbedding:
    """Embeds entire graph into quantum representation."""
    
    def __init__(self, num_nodes: int, n_qubits_per_node: int = 4, 
                 encoding_method: str = "angle"):
        """
        Initialize graph quantum embedding.
        
        Args:
            num_nodes: Number of nodes in the graph
            n_qubits_per_node: Qubits per node
            encoding_method: Quantum encoding scheme
        """
        self.num_nodes = num_nodes
        self.n_qubits_per_node = n_qubits_per_node
        self.encoding_method = encoding_method
        
        # Create encoder
        self.encoder = QuantumFeatureEncoder(n_qubits_per_node, encoding_method)
    
    def embed_node_features(self, node_features: np.ndarray) -> np.ndarray:
        """
        Embed node features of a single graph sample.
        
        Args:
            node_features: Shape (num_nodes, num_features)
        
        Returns:
            Quantum embeddings: Shape (num_nodes, n_qubits_per_node)
        """
        num_nodes, num_features = node_features.shape
        embeddings = np.zeros((num_nodes, self.n_qubits_per_node))
        
        for node_idx in range(num_nodes):
            embeddings[node_idx] = self.encoder.encode(node_features[node_idx])
        
        return embeddings
    
    def embed_batch(self, node_features_batch: np.ndarray) -> np.ndarray:
        """
        Embed a batch of graph samples.
        
        Args:
            node_features_batch: Shape (batch_size, num_nodes, num_features)
        
        Returns:
            Batch of quantum embeddings: (batch_size, num_nodes, n_qubits_per_node)
        """
        batch_size = node_features_batch.shape[0]
        embeddings = np.zeros((batch_size, self.num_nodes, self.n_qubits_per_node))
        
        for sample_idx in range(batch_size):
            embeddings[sample_idx] = self.embed_node_features(
                node_features_batch[sample_idx]
            )
        
        return embeddings


# ==============================================================================
# Main execution
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "="*70)
    print("PHASE 2: Quantum Feature Embedding")
    print("="*70)
    
    # Create sample features
    num_features = len(NODE_FEATURES)
    sample_features = np.random.randn(14, num_features)  # 14 nodes
    
    print(f"\nSample node features shape: {sample_features.shape}")
    print(f"First node features: {sample_features[0]}")
    
    # Test different encoding methods
    for method in ["angle", "amplitude", "iqp"]:
        print(f"\n--- Testing {method.upper()} Encoding ---")
        encoder = QuantumFeatureEncoder(n_qubits=4, encoding_method=method)
        
        # Encode single sample
        embedding = encoder.encode(sample_features[0])
        print(f"✓ Encoded single node: {embedding}")
        
        # Encode batch
        batch_embeddings = encoder.encode_batch(sample_features)
        print(f"✓ Batch encoding shape: {batch_embeddings.shape}")
    
    # Test graph-level embedding
    print(f"\n--- Graph-Level Quantum Embedding ---")
    graph_embedder = GraphQuantumEmbedding(num_nodes=14, n_qubits_per_node=4)
    
    # Embed single graph
    graph_embedding = graph_embedder.embed_node_features(sample_features)
    print(f"✓ Graph embedding shape: {graph_embedding.shape}")
    print(f"✓ First node quantum state: {graph_embedding[0]}")
    
    # Embed batch
    batch_graphs = np.random.randn(5, 14, num_features)
    batch_graph_embeddings = graph_embedder.embed_batch(batch_graphs)
    print(f"✓ Batch graph embeddings shape: {batch_graph_embeddings.shape}")
    
    print("\n" + "="*70)
    print("Phase 2 Complete! Features encoded in quantum states.")
    print("="*70)
