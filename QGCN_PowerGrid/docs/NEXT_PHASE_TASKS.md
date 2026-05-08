# Next Phase Tasks

## Immediate Improvements
1. Add one architecture figure to the simplified presentation.
2. Add one comparison table (QGCN vs classical baseline).
3. Add one limitations slide if presentation is for research review.

## Technical Upgrades
1. Add classical baseline model for direct performance comparison.
2. Run k-fold validation for stronger statistical confidence.
3. Add ablation experiments:
   - without message passing
   - without quantum embedding
   - varying qubits/layers

## Data Upgrades
1. Increase synthetic samples and stress scenarios.
2. Add event-based faults (line trip, generator outage, overload).
3. Add optional real or semi-real SCADA-like data format.

## Engineering Upgrades
1. Add experiment config presets (fast, balanced, full).
2. Save model checkpoints and reproducible run logs.
3. Build a single command runner for full pipeline.

## Documentation Upgrades
1. Add methodology diagram to README.
2. Add reproducibility checklist with exact commands.
3. Add one-page summary for non-technical stakeholders.

## Suggested Priority Order
1. Baseline comparison + ablation
2. Better experiments and validation
3. Presentation enhancements
4. Optional real-data integration
