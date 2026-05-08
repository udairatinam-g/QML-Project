"""
PHASE 3: Quantum Layer
Implements a Variational Quantum Circuit (VQC) for graph processing.
The circuit learns to extract patterns from quantum-embedded node features
and perform message passing between connected nodes.
"""

import numpy as np
import pennylane as qml
from pennylane import numpy as pnp
from typing import Tuple, List, Callable
from config import QUANTUM_CONFIG


class VariationalQuantumCircuit:
    """Variational Quantum Circuit for graph message passing."""
    
    def __init__(self, n_qubits: int = 4, n_layers: int = 3, 
                 entanglement_gate: str = "CNOT"):
        """
        Initialize VQC.
        
        Args:
            n_qubits: Number of qubits
            n_layers: Depth of quantum circuit (number of layers)
            entanglement_gate: "CNOT" or "CZ"
        """
        self.n_qubits = n_qubits
        self.n_layers = n_layers
        self.entanglement_gate = entanglement_gate
        
        # Device for quantum simulation
        self.dev = qml.device('default.qubit', wires=n_qubits)
        
        # Initialize parameters randomly
        # Two parameters per qubit per layer (RX and RZ angles)
        self.params = pnp.random.randn(n_layers, n_qubits, 2) * 0.1
        
        # For optimization
        self.params.requires_grad = True
        
        print(f"✓ Initialized Variational Quantum Circuit")
        print(f"  - Qubits: {n_qubits}")
        print(f"  - Layers: {n_layers}")
        print(f"  - Entanglement: {entanglement_gate}")
        print(f"  - Total parameters: {n_layers * n_qubits * 2}")
    
    def _apply_entanglement_layer(self, gate_type: str = "CNOT"):
        """Apply entanglement between qubits."""
        if gate_type == "CNOT":
            for i in range(self.n_qubits - 1):
                qml.CNOT(wires=[i, i + 1])
            # Add wrap-around
            if self.n_qubits > 2:
                qml.CNOT(wires=[self.n_qubits - 1, 0])
        
        elif gate_type == "CZ":
            for i in range(self.n_qubits - 1):
                qml.CZ(wires=[i, i + 1])
            if self.n_qubits > 2:
                qml.CZ(wires=[self.n_qubits - 1, 0])
    
    def _apply_rotation_layer(self, params_layer: np.ndarray):
        """Apply rotation layer with parameters."""
        for i in range(self.n_qubits):
            qml.RX(params_layer[i, 0], wires=i)
            qml.RZ(params_layer[i, 1], wires=i)
    
    def quantum_circuit(self, inputs: np.ndarray, params: np.ndarray) -> np.ndarray:
        """
        Quantum circuit that processes inputs.
        
        Uses a general structure:
        1. Encode input states
        2. Apply variational layers (rotation + entanglement)
        3. Measure expectation values
        
        Args:
            inputs: Quantum state from feature encoding, shape (n_qubits,)
            params: Trainable parameters, shape (n_layers, n_qubits, 2)
        
        Returns:
            Expectation values of Z measurements
        """
        @qml.qnode(self.dev)
        def circuit(x, p):
            # Initialize qubits with inputs
            for i in range(self.n_qubits):
                # Use amplitude encoding
                qml.RZ(x[i], wires=i)
            
            # Apply variational layers
            for layer in range(self.n_layers):
                # Rotation layer
                self._apply_rotation_layer(p[layer])
                
                # Entanglement layer
                self._apply_entanglement_layer(self.entanglement_gate)
            
            # Measure
            return [qml.expval(qml.PauliZ(i)) for i in range(self.n_qubits)]
        
        return np.array(circuit(inputs, params))
    
    def forward(self, inputs: np.ndarray) -> np.ndarray:
        """
        Forward pass through the quantum circuit.
        
        Args:
            inputs: Shape (n_qubits,) - quantum encoded features
        
        Returns:
            Output: Shape (n_qubits,) - processed quantum state
        """
        return self.quantum_circuit(inputs, self.params)
    
    def get_params(self) -> np.ndarray:
        """Get current parameters."""
        return np.copy(self.params)
    
    def set_params(self, new_params: np.ndarray):
        """Set new parameters."""
        self.params = pnp.array(new_params, requires_grad=True)
    
    def get_param_count(self) -> int:
        """Get total number of parameters."""
        return self.n_layers * self.n_qubits * 2


class QuantumMessagePassing:
    """Quantum circuit for graph message passing."""
    
    def __init__(self, n_qubits_per_node: int = 4, n_layers: int = 3):
        """
        Initialize quantum message passing.
        
        Args:
            n_qubits_per_node: Qubits per node
            n_layers: Circuit depth
        """
        self.n_qubits_per_node = n_qubits_per_node
        self.n_layers = n_layers
        
        # Quantum circuit for processing
        self.qvc = VariationalQuantumCircuit(
            n_qubits=n_qubits_per_node,
            n_layers=n_layers,
            entanglement_gate="CNOT"
        )
    
    def process_graph(self, node_embeddings: np.ndarray, 
                     adjacency_matrix: np.ndarray) -> np.ndarray:
        """
        Process graph using quantum message passing.
        
        Algorithm:
        1. Initialize node states from embeddings
        2. Apply quantum circuit to each node
        3. Incorporate neighbor information (message passing)
        4. Return updated node states
        
        Args:
            node_embeddings: Shape (num_nodes, n_qubits_per_node)
            adjacency_matrix: Shape (num_nodes, num_nodes)
        
        Returns:
            Updated node states: Shape (num_nodes, n_qubits_per_node)
        """
        num_nodes = node_embeddings.shape[0]
        updated_embeddings = np.zeros_like(node_embeddings)
        
        for node_idx in range(num_nodes):
            # Get quantum circuit output for this node
            node_output = self.qvc.forward(node_embeddings[node_idx])
            
            # Incorporate neighbor information (simple averaging)
            neighbors = np.where(adjacency_matrix[node_idx] > 0)[0]
            
            if len(neighbors) > 0:
                # Message from neighbors
                neighbor_messages = np.mean(
                    node_embeddings[neighbors], axis=0
                )
                
                # Combine own processing with neighbor info
                # (weight: 0.7 own processing, 0.3 neighbor average)
                updated_embeddings[node_idx] = (0.7 * node_output + 
                                               0.3 * neighbor_messages)
            else:
                updated_embeddings[node_idx] = node_output
        
        return updated_embeddings
    
    def get_circuit_params(self) -> np.ndarray:
        """Get VQC parameters."""
        return self.qvc.get_params()
    
    def set_circuit_params(self, params: np.ndarray):
        """Set VQC parameters."""
        self.qvc.set_params(params)


class QuantumGraphConvolution:
    """Complete Quantum Graph Convolutional Network layer."""
    
    def __init__(self, n_nodes: int, n_qubits_per_node: int = 4, 
                 n_layers: int = 3):
        """
        Initialize QGCN layer.
        
        Args:
            n_nodes: Number of graph nodes
            n_qubits_per_node: Qubits per node
            n_layers: VQC depth
        """
        self.n_nodes = n_nodes
        self.n_qubits_per_node = n_qubits_per_node
        
        self.message_passer = QuantumMessagePassing(
            n_qubits_per_node=n_qubits_per_node,
            n_layers=n_layers
        )
        
        # Classical output layer (learned mapping from quantum state to scalar)
        # For each node: maps n_qubits -> 1 scalar value
        self.output_weights = np.random.randn(n_qubits_per_node) * 0.1
        self.output_bias = 0.0
    
    def forward(self, node_embeddings: np.ndarray, 
                adjacency_matrix: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Forward pass through QGCN layer.
        
        Args:
            node_embeddings: Shape (num_nodes, n_qubits_per_node)
            adjacency_matrix: Shape (num_nodes, num_nodes)
        
        Returns:
            quantum_states: Processed quantum states
            classical_outputs: Classical prediction for each node
        """
        # Quantum message passing
        quantum_states = self.message_passer.process_graph(
            node_embeddings, adjacency_matrix
        )
        
        # Classical readout: map quantum states to scalar values
        classical_outputs = np.dot(quantum_states, self.output_weights) + self.output_bias
        
        return quantum_states, classical_outputs
    
    def get_params(self) -> dict:
        """Get all trainable parameters."""
        return {
            "quantum_params": self.message_passer.get_circuit_params(),
            "output_weights": self.output_weights,
            "output_bias": self.output_bias
        }
    
    def set_params(self, params: dict):
        """Set trainable parameters."""
        self.message_passer.set_circuit_params(params["quantum_params"])
        self.output_weights = params["output_weights"]
        self.output_bias = params["output_bias"]


# ==============================================================================
# Main execution
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "="*70)
    print("PHASE 3: Quantum Graph Convolutional Network")
    print("="*70)
    
    # Test VQC
    print("\n--- Variational Quantum Circuit ---")
    vqc = VariationalQuantumCircuit(n_qubits=4, n_layers=3)
    
    sample_input = np.array([0.1, -0.2, 0.3, -0.1])
    output = vqc.forward(sample_input)
    print(f"✓ VQC input: {sample_input}")
    print(f"✓ VQC output: {output}")
    print(f"✓ Parameter count: {vqc.get_param_count()}")
    
    # Test message passing
    print("\n--- Quantum Message Passing ---")
    msg_passer = QuantumMessagePassing(n_qubits_per_node=4, n_layers=3)
    
    # Synthetic graph
    num_nodes = 5
    node_embeddings = np.random.randn(num_nodes, 4)
    adjacency_matrix = np.array([
        [0, 1, 1, 0, 0],
        [1, 0, 1, 1, 0],
        [1, 1, 0, 0, 1],
        [0, 1, 0, 0, 1],
        [0, 0, 1, 1, 0]
    ], dtype=float)
    
    print(f"✓ Graph: {num_nodes} nodes, {int(np.sum(adjacency_matrix) / 2)} edges")
    
    updated = msg_passer.process_graph(node_embeddings, adjacency_matrix)
    print(f"✓ Updated node embeddings shape: {updated.shape}")
    print(f"✓ First node before: {node_embeddings[0]}")
    print(f"✓ First node after:  {updated[0]}")
    
    # Test QGCN layer
    print("\n--- Quantum Graph Convolutional Layer ---")
    qgcn = QuantumGraphConvolution(n_nodes=num_nodes, n_qubits_per_node=4, n_layers=3)
    
    quantum_states, classical_outputs = qgcn.forward(node_embeddings, adjacency_matrix)
    print(f"✓ Quantum states shape: {quantum_states.shape}")
    print(f"✓ Classical outputs shape: {classical_outputs.shape}")
    print(f"✓ Classical outputs (node predictions): {classical_outputs}")
    
    # Get parameters
    params = qgcn.get_params()
    print(f"\n✓ Total quantum parameters: {params['quantum_params'].size}")
    print(f"✓ Output weights: {params['output_weights'].shape}")
    print(f"✓ Output bias: {params['output_bias']}")
    
    print("\n" + "="*70)
    print("Phase 3 Complete! Quantum processing layer ready.")
    print("="*70)
