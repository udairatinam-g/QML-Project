import matplotlib.pyplot as plt
import networkx as nx
import os

outputs_dir = r"C:\Users\Udai Ratinam G\Downloads\QML Project\QGCN_PowerGrid\outputs"
os.makedirs(outputs_dir, exist_ok=True)

# 1. Architecture Flow Diagram
plt.figure(figsize=(10, 6))
G = nx.DiGraph()

G.add_node("Data Modeling\n(IEEE 14-Bus)", pos=(0, 2))
G.add_node("Telemetry Extraction\n(V, Theta, P, Q)", pos=(1, 2))
G.add_node("Quantum Feature\nEncoder (Pennylane)", pos=(2, 2))
G.add_node("Hilbert Space\nMapping", pos=(3, 2))
G.add_node("Message Passing\n(GCN Layer)", pos=(4, 2))
G.add_node("Risk Classification", pos=(5, 2))

G.add_edge("Data Modeling\n(IEEE 14-Bus)", "Telemetry Extraction\n(V, Theta, P, Q)")
G.add_edge("Telemetry Extraction\n(V, Theta, P, Q)", "Quantum Feature\nEncoder (Pennylane)")
G.add_edge("Quantum Feature\nEncoder (Pennylane)", "Hilbert Space\nMapping")
G.add_edge("Hilbert Space\nMapping", "Message Passing\n(GCN Layer)")
G.add_edge("Message Passing\n(GCN Layer)", "Risk Classification")

pos = nx.get_node_attributes(G, 'pos')
nx.draw(G, pos, with_labels=True, node_color='lightblue', 
        node_size=6000, font_size=9, font_weight='bold', 
        arrowsize=20, edge_color='gray')

plt.title("Pipeline Flow of QGCN Implementation", fontsize=14, pad=20)
plt.savefig(os.path.join(outputs_dir, "08_architecture_flow.png"), bbox_inches='tight', dpi=300)
plt.close()

# 2. Quantum Circuit Abstraction
fig, ax = plt.subplots(figsize=(8, 4))
ax.axis('off')
ax.text(0.1, 0.8, "|0⟩ ───[H]───[Rz(x1)]───●───────", fontsize=14)
ax.text(0.1, 0.6, "|0⟩ ───[H]───[Rz(x2)]───|───────", fontsize=14)
ax.text(0.1, 0.4, "|0⟩ ───[H]───[Rz(x3)]───X───●───", fontsize=14)
ax.text(0.1, 0.2, "|0⟩ ───[H]───[Rz(x4)]───────X───", fontsize=14)

ax.text(0.5, 0.9, "IQP Encoding Circuit Topology", fontsize=16, weight='bold')
plt.savefig(os.path.join(outputs_dir, "09_quantum_circuit_diagram.png"), bbox_inches='tight', dpi=300)
plt.close()

print("Generated architecture diagrams successfully.")
