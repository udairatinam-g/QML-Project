import PyPDF2
import re

pdf_path = r"C:\Users\Udai Ratinam G\Downloads\QML Project\QGCN_PowerGrid\deliverables\QGCN_Formal_Project_Report_v6.docx.pdf"

queries = [
    "ABSTRACT",
    "TABLE OF CONTENTS",
    "CHAPTER 1 - INTRODUCTION",
    "1.1 Overview of the Software Pipeline",
    "1.2 Core Dependencies and Simulation Stack",
    "1.3 Project Implementation Goals",
    "CHAPTER 2 - DATA MODELING",
    "2.1 IEEE 14-Bus Topology",
    "2.2 Telemetry Feature Normalization",
    "CHAPTER 3 - QUANTUM FEATURE ENCODER",
    "3.1 PennyLane Simulator Configuration",
    "3.2 Core Code: Angle Encoding Circuit",
    "3.3 Core Code: IQP Encoding Architecture",
    "CHAPTER 4 - CLASSICAL MESSAGE PASSING",
    "4.1 Adjacency Matrix Multiplication",
    "4.2 Hybrid Gradient Computation",
    "CHAPTER 5 - RESULTS",
    "5.1 Model Convergence Analysis",
    "5.2 Spatial Risk Visualization",
    "5.3 Baseline Comparison Analysis",
    "REFERENCES"
]

results = {q: None for q in queries}

try:
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            text = reader.pages[page_num].extract_text()
            if text:
                text = text.replace('\n', ' ')
                for q in queries:
                    if results[q] is None and q in text:
                        # PyPDF2 is 0-indexed, Word usually prints page 1 as physical page 1
                        results[q] = page_num + 1
                        
    for q in queries:
        print(f"{q}: {results[q]}")
except Exception as e:
    print(f"Error: {e}")
