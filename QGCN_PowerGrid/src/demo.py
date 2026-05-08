"""
CPU-friendly QGCN demo.
Runs end-to-end inference with 0 training epochs and generates reproducible outputs.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_curve, auc
from sklearn.model_selection import train_test_split

from phase1_data_modeling import PowerGridSimulator
from phase4_training import QGCNModel
from config import GRID_CONFIG, QUANTUM_CONFIG, TRAINING_CONFIG


def ensure_dirs() -> None:
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("docs", exist_ok=True)


def plot_prediction_distribution(pred_normal: np.ndarray, pred_failure: np.ndarray) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(pred_normal, bins=14, alpha=0.65, label="Normal Grid States",
            color="#4ECDC4", edgecolor="black", linewidth=1.2)
    ax.hist(pred_failure, bins=14, alpha=0.65, label="Failed Grid States",
            color="#FF6B6B", edgecolor="black", linewidth=1.2)
    ax.axvline(0.5, color="black", linestyle="--", linewidth=2.2, label="Decision Threshold")
    ax.set_xlabel("Predicted Failure Probability", fontsize=12, fontweight="bold")
    ax.set_ylabel("Frequency", fontsize=12, fontweight="bold")
    ax.set_title("QGCN Zero-Epoch Inference Distribution", fontsize=13, fontweight="bold")
    ax.legend(fontsize=11, framealpha=0.95)
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig("outputs/03_prediction_distribution.png", dpi=150, bbox_inches="tight")
    plt.close()


def plot_risk_heatmap(grid: PowerGridSimulator, node_risk: np.ndarray) -> None:
    import networkx as nx

    fig, ax = plt.subplots(1, 1, figsize=(12, 9))
    pos = nx.spring_layout(grid.graph, k=2.5, iterations=50, seed=42)

    nodes = nx.draw_networkx_nodes(
        grid.graph,
        pos,
        nodelist=list(grid.graph.nodes()),
        node_color=node_risk,
        node_size=1000,
        cmap="RdYlGn_r",
        ax=ax,
        vmin=0,
        vmax=1,
    )
    nx.draw_networkx_edges(grid.graph, pos, width=2, alpha=0.6, ax=ax)
    nx.draw_networkx_labels(grid.graph, pos, font_size=10, font_weight="bold", ax=ax)

    ax.set_title("Node Risk from Quantum State Magnitude", fontsize=13, fontweight="bold", pad=20)
    ax.axis("off")
    plt.colorbar(nodes, ax=ax, label="Relative Risk Score", shrink=0.8)
    plt.tight_layout()
    plt.savefig("outputs/04_grid_risk_heatmap.png", dpi=150, bbox_inches="tight")
    plt.close()


def plot_quantum_states(states: np.ndarray) -> None:
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(states, cmap="coolwarm", aspect="auto", vmin=-1.0, vmax=1.0)
    ax.set_xlabel("Qubit Index", fontsize=12, fontweight="bold")
    ax.set_ylabel("Substation Node", fontsize=12, fontweight="bold")
    ax.set_title("Quantum State Expectations Across Grid Nodes", fontsize=13, fontweight="bold")
    ax.set_yticks(range(states.shape[0]))
    ax.set_yticklabels([f"Bus {i + 1}" for i in range(states.shape[0])])
    ax.set_xticks(range(states.shape[1]))
    ax.set_xticklabels([f"Q{i}" for i in range(states.shape[1])])
    plt.colorbar(im, ax=ax, label="Z-basis Expectation")
    plt.tight_layout()
    plt.savefig("outputs/05_quantum_states.png", dpi=150, bbox_inches="tight")
    plt.close()


def plot_roc(y_true: np.ndarray, y_score: np.ndarray) -> float:
    fpr, tpr, _ = roc_curve(y_true, y_score)
    roc_auc = auc(fpr, tpr)

    fig, ax = plt.subplots(figsize=(9, 8))
    ax.plot(fpr, tpr, color="#FF6B6B", lw=3, label=f"QGCN (AUC = {roc_auc:.3f})")
    ax.plot([0, 1], [0, 1], color="gray", lw=2.5, linestyle="--", label="Random Classifier")
    ax.fill_between(fpr, tpr, alpha=0.15, color="#FF6B6B")
    ax.set_xlim([-0.02, 1.02])
    ax.set_ylim([-0.02, 1.02])
    ax.set_xlabel("False Positive Rate", fontsize=12, fontweight="bold")
    ax.set_ylabel("True Positive Rate", fontsize=12, fontweight="bold")
    ax.set_title("ROC Curve - Zero-Epoch QGCN", fontsize=13, fontweight="bold")
    ax.legend(loc="lower right", fontsize=12, framealpha=0.95)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("outputs/06_roc_curve.png", dpi=150, bbox_inches="tight")
    plt.close()

    return roc_auc


def write_execution_summary(metrics: dict, roc_auc: float) -> None:
    lines = [
        "# Execution Summary (CPU, 0 Epochs)",
        "",
        "This run uses the real QGCN forward path with **no training**.",
        "",
        "## Runtime Mode",
        f"- epochs: {TRAINING_CONFIG['num_epochs']}",
        "- device: PennyLane default.qubit simulator (CPU)",
        "- purpose: reproducible architecture/demo outputs without GPU",
        "",
        "## Metrics (untrained model)",
        f"- Accuracy: {metrics['accuracy']:.4f}",
        f"- Precision: {metrics['precision']:.4f}",
        f"- Recall: {metrics['recall']:.4f}",
        f"- F1: {metrics['f1']:.4f}",
        f"- AUC: {roc_auc:.4f}",
        "",
        "## Notes",
        "- These metrics are from zero-epoch inference, not optimized training.",
        "- Outputs are suitable for architecture explanation, reproducibility, and code walkthrough.",
    ]

    with open("docs/EXECUTION_SUMMARY.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main() -> None:
    np.random.seed(TRAINING_CONFIG["random_seed"])
    ensure_dirs()

    print("\n" + "=" * 80)
    print("QGCN Power Grid - CPU Inference Demo (No Epochs)")
    print("=" * 80)

    grid = PowerGridSimulator(config=GRID_CONFIG)
    grid.visualize_grid(save_path="outputs/01_grid_topology.png")

    x, y = grid.generate_node_features(num_samples=250, failure_injection=True)
    _, x_test, _, y_test = train_test_split(
        x,
        y,
        test_size=TRAINING_CONFIG["validation_split"],
        random_state=TRAINING_CONFIG["random_seed"],
    )

    model = QGCNModel(
        num_nodes=GRID_CONFIG["num_buses"],
        n_qubits_per_node=QUANTUM_CONFIG["n_qubits"],
        n_layers=QUANTUM_CONFIG["n_layers"],
    )

    model.plot_history()

    # Limit number of inference samples to keep demo responsive on CPU
    max_eval = min(12, x_test.shape[0])
    print(f"Running inference on {max_eval} test samples (of {x_test.shape[0]}) to keep demo fast")
    preds = []
    quantum_states_all = []
    for i in range(max_eval):
        print(f"  Inference sample {i+1}/{max_eval}", end='\r')
        p, q_states = model.forward(x_test[i])
        preds.append(p)
        quantum_states_all.append(q_states)
    print()

    preds = np.array(preds)
    quantum_states_all = np.array(quantum_states_all)
    pred_binary = (preds > 0.5).astype(int)

    # Evaluate on the same subset used for inference
    y_eval = y_test[:max_eval]

    # Use the evaluated subset for metric calculations
    metrics = {
        "accuracy": accuracy_score(y_eval, pred_binary),
        "precision": precision_score(y_eval, pred_binary, zero_division=0),
        "recall": recall_score(y_eval, pred_binary, zero_division=0),
        "f1": f1_score(y_eval, pred_binary, zero_division=0),
    }

    pred_normal = preds[y_eval == 0]
    pred_failure = preds[y_eval == 1]

    if pred_normal.size == 0:
        pred_normal = np.array([0.0])
    if pred_failure.size == 0:
        pred_failure = np.array([1.0])
    plot_prediction_distribution(pred_normal, pred_failure)

    # Use average absolute quantum magnitude as node risk proxy across evaluated set.
    node_risk_raw = np.mean(np.abs(quantum_states_all), axis=(0, 2))
    node_risk = (node_risk_raw - node_risk_raw.min()) / (np.ptp(node_risk_raw) + 1e-8)
    plot_risk_heatmap(grid, node_risk)

    plot_quantum_states(quantum_states_all[0])
    roc_auc = plot_roc(y_eval, preds)

    write_execution_summary(metrics, roc_auc)

    print("\nGenerated files:")
    print("- outputs/01_grid_topology.png")
    print("- outputs/02_training_history.png")
    print("- outputs/03_prediction_distribution.png")
    print("- outputs/04_grid_risk_heatmap.png")
    print("- outputs/05_quantum_states.png")
    print("- outputs/06_roc_curve.png")
    print("- docs/EXECUTION_SUMMARY.md")

    print("\nMetrics (zero-epoch inference):")
    print(f"- Accuracy:  {metrics['accuracy']:.4f}")
    print(f"- Precision: {metrics['precision']:.4f}")
    print(f"- Recall:    {metrics['recall']:.4f}")
    print(f"- F1:        {metrics['f1']:.4f}")
    print(f"- AUC:       {roc_auc:.4f}")


if __name__ == "__main__":
    main()
