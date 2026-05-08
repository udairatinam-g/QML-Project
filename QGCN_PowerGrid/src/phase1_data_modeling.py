"""
PHASE 1: Data Modeling
Creates a synthetic IEEE 14-bus power grid as a NetworkX graph.
Nodes represent substations, edges represent transmission lines.
"""

import networkx as nx
import numpy as np
from typing import Tuple, Dict, List
from config import GRID_CONFIG, NODE_FEATURES, DATA_CONFIG


class PowerGridSimulator:
    """Simulates a power grid as a graph structure."""
    
    def __init__(self, config: dict = None):
        """Initialize the power grid simulator."""
        self.config = config or GRID_CONFIG
        self.graph = None
        self.node_features_history = []
        self.failure_labels = []
        self._create_ieee_14_bus_graph()
    
    def _create_ieee_14_bus_graph(self):
        """
        Create IEEE 14-Bus test system topology.
        Based on standard power systems test cases.
        """
        self.graph = nx.Graph()
        
        # Add all buses (nodes)
        for bus_id in range(1, self.config["num_buses"] + 1):
            self.graph.add_node(bus_id, bus_type="load")
        
        # Define generator buses (typically include slack bus)
        generator_buses = [1, 2, 3, 6, 8]
        for gen_bus in generator_buses:
            self.graph.nodes[gen_bus]["bus_type"] = "generator"
        
        # Define transmission lines (edges) - IEEE 14-bus standard topology
        lines = [
            (1, 2), (1, 5), (2, 3), (2, 4), (2, 5),
            (3, 4), (4, 5), (4, 7), (4, 9), (5, 6),
            (6, 11), (6, 12), (6, 13), (7, 8), (7, 9),
            (9, 10), (9, 14), (10, 11), (12, 13), (13, 14)
        ]
        
        for i, (u, v) in enumerate(lines):
            # Add transmission line properties
            self.graph.add_edge(u, v, 
                              line_id=i+1,
                              resistance=np.random.uniform(0.01, 0.05),
                              reactance=np.random.uniform(0.1, 0.3),
                              capacity=np.random.uniform(1.0, 2.0))
        
        print(f"✓ Created IEEE 14-Bus Graph with {self.graph.number_of_nodes()} nodes "
              f"and {self.graph.number_of_edges()} edges")
    
    def get_graph_info(self) -> Dict:
        """Get basic information about the graph."""
        return {
            "num_nodes": self.graph.number_of_nodes(),
            "num_edges": self.graph.number_of_edges(),
            "density": nx.density(self.graph),
            "average_degree": np.mean([d for n, d in self.graph.degree()]),
            "is_connected": nx.is_connected(self.graph),
            "diameter": nx.diameter(self.graph) if nx.is_connected(self.graph) else None,
        }
    
    def generate_node_features(self, num_samples: int = 100, 
                              failure_injection: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate synthetic node features for power grid.
        
        Features per node:
        - Voltage magnitude (0.9-1.1 p.u.)
        - Voltage angle (-0.5 to 0.5 rad)
        - Active power injection (-2 to 2 p.u.)
        - Reactive power injection (-1 to 1 p.u.)
        - Load level (0-1)
        
        Returns:
            node_features: (num_samples, num_nodes, num_features)
            failure_labels: (num_samples,) binary labels
        """
        num_nodes = self.graph.number_of_nodes()
        num_features = len(NODE_FEATURES)
        
        node_features = np.zeros((num_samples, num_nodes, num_features))
        failure_labels = np.zeros(num_samples)
        
        feature_keys = list(NODE_FEATURES.keys())
        noise_level = DATA_CONFIG["noise_level"]
        failure_prob = DATA_CONFIG["failure_probability"]
        
        for sample_idx in range(num_samples):
            features_dict = {}
            
            # Generate features for each node
            for feat_idx, feature_name in enumerate(feature_keys):
                feature_config = NODE_FEATURES[feature_name]
                min_val = feature_config["min"]
                max_val = feature_config["max"]
                
                # Generate base values
                base_value = np.random.uniform(min_val, max_val, num_nodes)
                
                # Add Gaussian noise
                noise = np.random.normal(0, noise_level * (max_val - min_val), num_nodes)
                values = np.clip(base_value + noise, min_val, max_val)
                
                node_features[sample_idx, :, feat_idx] = values
                features_dict[feature_name] = values
            
            # Generate failure label (40% probability if severe conditions)
            voltage_violations = np.mean(
                (node_features[sample_idx, :, 0] < 0.92) | 
                (node_features[sample_idx, :, 0] > 1.08)
            )
            
            failure_labels[sample_idx] = int(
                voltage_violations > 0.3 or
                np.random.random() < failure_prob
            )
        
        self.node_features_history = node_features
        self.failure_labels = failure_labels
        
        return node_features, failure_labels
    
    def get_adjacency_matrix(self) -> np.ndarray:
        """Get adjacency matrix of the graph."""
        return nx.to_numpy_array(self.graph)
    
    def get_edge_index(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get edge indices for PyTorch Geometric format."""
        edges = np.array(list(self.graph.edges())).T - 1  # 0-indexed
        return edges[0], edges[1]
    
    def visualize_grid(self, save_path: str = None):
        """Visualize the power grid graph."""
        try:
            import matplotlib.pyplot as plt
            
            pos = nx.spring_layout(self.graph, k=2, iterations=50, seed=42)
            
            plt.figure(figsize=(12, 10))
            
            # Draw generator nodes
            generator_nodes = [n for n in self.graph.nodes() 
                             if self.graph.nodes[n].get("bus_type") == "generator"]
            load_nodes = [n for n in self.graph.nodes() 
                        if self.graph.nodes[n].get("bus_type") == "load"]
            
            nx.draw_networkx_nodes(self.graph, pos, nodelist=generator_nodes,
                                  node_color='red', node_size=500, label='Generators')
            nx.draw_networkx_nodes(self.graph, pos, nodelist=load_nodes,
                                  node_color='lightblue', node_size=500, label='Loads')
            
            nx.draw_networkx_edges(self.graph, pos, width=2, alpha=0.6)
            nx.draw_networkx_labels(self.graph, pos, font_size=10)
            
            plt.title("IEEE 14-Bus Power Grid Topology", fontsize=14, fontweight='bold')
            plt.legend(loc='upper left')
            plt.axis('off')
            
            if save_path:
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                print(f"✓ Grid visualization saved to {save_path}")
            else:
                plt.show()
            
        except ImportError:
            print("⚠ Matplotlib not available for visualization")


# ==============================================================================
# Main execution
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "="*70)
    print("PHASE 1: Power Grid Data Modeling")
    print("="*70)
    
    # Initialize simulator
    simulator = PowerGridSimulator()
    
    # Print graph information
    print("\nGraph Information:")
    graph_info = simulator.get_graph_info()
    for key, value in graph_info.items():
        print(f"  {key}: {value}")
    
    # Generate synthetic data
    print("\nGenerating synthetic node features...")
    node_features, failure_labels = simulator.generate_node_features(
        num_samples=DATA_CONFIG["num_samples"],
        failure_injection=True
    )
    
    print(f"✓ Generated {node_features.shape[0]} samples with {node_features.shape[1]} nodes "
          f"and {node_features.shape[2]} features per node")
    print(f"✓ Failure labels distribution: {np.bincount(failure_labels)}")
    print(f"  - Normal: {np.sum(failure_labels == 0)} samples")
    print(f"  - Failure: {np.sum(failure_labels == 1)} samples")
    
    # Get graph structure
    print("\nGraph structure formats:")
    adj_matrix = simulator.get_adjacency_matrix()
    print(f"✓ Adjacency matrix shape: {adj_matrix.shape}")
    
    edge_idx_0, edge_idx_1 = simulator.get_edge_index()
    print(f"✓ Edge indices: {edge_idx_0.shape[0]} edges found")
    
    # Visualize grid
    print("\nVisualizing grid topology...")
    simulator.visualize_grid(save_path="power_grid_topology.png")
    
    print("\n" + "="*70)
    print("Phase 1 Complete! Data is ready for quantum embedding.")
    print("="*70)
