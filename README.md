
# 📊 Quantifying Clean Energy in Alberta

A simulation-based model that visualizes the distribution of clean vs. traditional energy across 42 regions in Alberta using real-time load and generation data. This project uses **PyPSA** to simulate the power flow, calculates clean energy ratios, and maps equity disparities across the grid.

---

## ⚙️ Features

- Real-time grid simulation using **PyPSA**
- Inputs from:
  - Hourly load data
  - Generation capacities
  - Geographic coordinates of nodes
- Visualizes:
  - Power flow between regions
  - Generator types (wind, solar, hydro, gas, bio)
  - Line loading and clean energy percentages
- Designed to support **policy analysis and infrastructure planning**

---

## 📁 File Structure

```
.
├── DisplayPYPSA.py                   # Main simulation and visualization script
└── Data/
    ├── Generation Data.xlsx          # Generator types and capacities
    ├── hourly_load_data_by_area.xlsx # Hourly load data per region
    └── Load Data With Coordinates.xlsx # Node coordinates for mapping
```

---

## ▶️ How to Run

1. Ensure all files are in place and the `Data/` folder contains the required Excel sheets.
2. Install dependencies:
   ```bash
   pip install pypsa pandas matplotlib cartopy openpyxl
   ```
3. Run the main script:
   ```bash
   python DisplayPYPSA.py
   ```
4. When prompted, enter a **date** (`YYYY-MM-DD`) and **time** (`HH:00:00`) to simulate.
5. An interactive map will be generated showing:
   - Generator locations and sizes
   - Line loadings
   - Energy type breakdown
   - Region-wise clean energy ratios

---

## 📦 Dependencies

- Python 3.8+
- PyPSA
- pandas
- numpy
- matplotlib
- cartopy
- openpyxl
- xlrd
- linopy

---

## 🧠 Project Objective

This tool supports equitable power distribution in Alberta by helping:
- Identify underserved regions
- Quantify clean energy access relative to income
- Guide placement of future renewable energy projects

---

## 📝 Credits

Developed by: **Moaz Abdelmonem**  
Capstone Project, University of Alberta (ECE 491)
