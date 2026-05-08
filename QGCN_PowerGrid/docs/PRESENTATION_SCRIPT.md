# Presentation Script (7 Slides)

Use this script with QGCN_PowerGrid_Presentation_Simplified.pptx.

## Slide 1: Title
"This project is about using Quantum Graph Convolutional Networks to improve power grid reliability. The main goal is to predict risky grid conditions early and help operators prevent failures."

## Slide 2: Abstract
"In simple terms, we treat the power grid as a network and train a model to identify unstable patterns. The model combines graph-based learning with quantum feature processing and outputs a risk score that can be used as an early warning signal."

## Slide 3: Problem Statement and Motivation
"Power grids are connected systems. A problem at one substation can affect others. So we need a model that understands not only local values like voltage and load, but also how disturbances spread through network connections."

## Slide 4: Simple Theory Behind the Model
"Each substation has key electrical features. We convert these features into a quantum-friendly representation, then process them to capture complex interactions. The benefit is richer feature learning for difficult non-linear behaviors."

## Slide 5: Model Architecture in Simple Steps
"There are four main steps: feature encoding, quantum processing, message passing between connected nodes, and final risk prediction. This pipeline mirrors how information flows in real power systems."

## Slide 6: Implementation Blueprint
"Implementation is done in four phases:
1) Data modeling on IEEE 14-bus graph,
2) Quantum embedding,
3) Quantum message passing,
4) Training and evaluation.
This structure makes the project modular and easy to extend."

## Slide 7: Results and Impact
"The model achieves strong performance and gives practical value by generating early warnings. In operations, this can support load balancing, rerouting, and preventive control actions to reduce outage risk."

## 30-Second Closing
"This project shows how quantum-enhanced graph learning can be applied to critical infrastructure. It provides a clear implementation path, good predictive performance, and practical value for smart-grid reliability."

## Common Viva Questions and Short Answers

Q1. Why use a graph model?
A: Because the grid is naturally a network of connected substations and lines.

Q2. Why include quantum processing?
A: It helps represent complex interactions in a compact way and can improve difficult classification boundaries.

Q3. Is this deployable today?
A: Yes, as a decision-support module in simulation and control-room analytics. Hardware quantum deployment is a future extension.

Q4. What is the major contribution?
A: A complete phase-wise QGCN implementation for power grid reliability with clear practical interpretation.
