# Quantum Graph Convolutional Networks for Power Grid Reliability

This repository contains a complete hybrid quantum-graph project focused on power-grid risk prediction.

## Project Status
- Deliverable pipeline: working
- Key outputs: generated and reproducible
- Presentation and writeup: generated in deliverables

## Clean Structure
- src/: core model and experiments
- scripts/: utility generators (PPT, DOCX)
- outputs/: generated figures
- deliverables/: final PPT and DOCX
- docs/: reports and theory notes
- notebooks/: interactive notebook

## Run Commands
```powershell
python src\demo.py
python src\baseline_comparison.py
python scripts\create_presentation.py
python scripts\create_project_writeup_doc.py
```

## One-Click Runner
```powershell
powershell -ExecutionPolicy Bypass -File .\run_deliverables.ps1
```

## Main Pipeline Note
`python src\main.py` now defaults to CPU-friendly mode with 0 epochs (no training loop).
This ensures the full pipeline runs without GPU requirements while still executing the real quantum forward path.

## Core Output Files
- outputs/01_grid_topology.png
- outputs/02_training_history.png
- outputs/03_prediction_distribution.png
- outputs/04_grid_risk_heatmap.png
- outputs/05_quantum_states.png
- outputs/06_roc_curve.png
- outputs/07_baseline_comparison.png
- docs/EXECUTION_SUMMARY.md
- deliverables/QGCN_PowerGrid_Presentation_Simplified.pptx
- deliverables/QGCN_Project_Writeup_Udai_Ratinam_G.docx
