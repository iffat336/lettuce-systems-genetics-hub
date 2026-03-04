# 🌱 Unified PhD Research Hub: Seed Mechanics & AI Agriculture Suite

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/) 
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)
![Architecture-4.0](https://img.shields.io/badge/Industry-4.0-green)

This platform is a **Unified PhD Research Hub** developed for the PhD interview process at the **Poznań University of Life Sciences (Faculty of Environmental and Mechanical Engineering)**. 

The project bridges the gap between **Computational Mechanics** (Prof. Tomasz Garbowski and Prof. Anna Maria Szymczak-Graczyk) and **Agricultural Biosystems**, demonstrating a holistic approach to Agriculture 4.0.

---

## 🔬 Project Pillars & Core Modules

### 1. Material Mechanics (The Digital Twin)
The flagship module of the hub, focusing on the **Hygrothermal Performance** of biological materials.
*   **Surrogate Modeling**: Translates complex, high-latency Finite Element Method (FEM) simulations into high-speed **Artificial Neural Network (ANN)** models.
*   **Real-Time stability Analysis**: Predictive modeling of moisture diffusion and mechanical stability under varying loads.
*   **3D Stability Landscape**: Interactive visualizations of the material's response across the entire hygrothermal spectrum.

### 2. Research Productivity (AI Assistant & Diagnostics)
Integrating modern AI tools to enhance research efficiency and Human-Machine Interaction (HMI).
*   **AgriBot Assistant**: A specialized NLP-driven chatbot for instant agricultural guidance and research query handling.
*   **Disease Detective**: AI Computer Vision simulation for early-stage diagnostic monitoring of material/plant health.

### 3. Urban Dynamics (Computational Urban Mechanics)
Translating multiscale material laws to urban complexity.
*   **Multiscale Homogenization**: Mapping micro-scale building material properties (anisotropy/porosity) to macro-scale urban thermal and mechanical stability.
*   **Inverse Analysis Loop**: A simulated solver for predicting unobservable material parameters from sensor data, utilizing convergence-based optimization.
*   **Stress/Strain Landscapes**: 3D visualizations of homogenized stress distribution across an urban grid.

---

## 📚 Scientific Foundations & Equations

This project is built upon rigorous mathematical and biological foundations:
- **Ellis-Roberts Longevity Equations**: The gold standard for predicting seed viability over time.
- **Harrington’s Rule of Thumb**: For safe storage temperature and humidity interaction.
- **Arrhenius-inspired Diffusion Models**: To simulate moisture ingress during environmental cycles.
- **Inverse Analysis**: Implicitly used to determine material homogenization through surrogate mapping.

---

## 🛠️ Technical Architecture & Stack

- **Dashboard Framework**: [Streamlit](https://streamlit.io/) (Premium multi-page navigation)
- **Machine Learning**: Scikit-Learn (MLP Regressors, Random Forests)
- **Data Visualization**: [Plotly](https://plotly.com/) (Interactive 3D surfaces and Gauges)
- **Computational Core**: NumPy & SciPy (Physics-informed logic)
- **Image Processing**: Pillow (Diagnostics simulation)

### Project Layout
- `pages/`: Interactive modules (Dashboard, AgriBot, Logistics, etc.)
- `src/research_suite/`: Core logic for the unified AI modules.
- `src/seed_science.py`: Implementation of scientific equations.
- `config.py`: Centralized research constants and seed-type definitions.

---

## 🚀 Installation & Execution

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/iffat336/AI_Agriculture_Suite-.git
   cd AI_Agriculture_Suite-
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the Hub**:
   ```bash
   streamlit run app.py
   ```

---

## 🎓 PhD Candidate Value Proposition

As a researcher, this project demonstrates my readiness to:
*   **Master Surrogate Modeling**: Solve computational bottlenecks in **Computational Mechanics**.
*   **Design Interdisciplinary Architectures**: Bridge engineering with AI and Biology.
*   **Deploy Professional Research Tools**: Communicate sophisticated concepts through premium visualization and interactive software.

---
*Developed by **Iffat Nazir** - Bridging Computational Mechanics and Agriculture 4.0.*
