# ReactoN — Hydrogen Generation System Analysis Platform

**Status:** TRL 4 (Laboratory-Validated) | **Funding:** World Bank SOGREEN | **Recognition:** EU Seal of Excellence

---

## Overview

ReactoN is an advanced, physics- and chemistry-grounded computational analysis and integration platform for ASRHÜR's patented aluminum-water reaction (AWR) hydrogen generation technology.

Designed to serve as the software bridge between laboratory science (TRL 4) and field-validated industrial deployment (TRL 5), ReactoN models raw reaksiyon kinetics, phase equilibria, and pressure vessel sizing, and optimizes multi-criteria operating parameters. It exposes these core computational routines via a high-performance, automated **FastAPI** web service.

### What it does:
- **Kinetics Simulation:** Implements the *Shrinking Core Model (SCM)* to simulate reaction progress ($\alpha$) across varying particle size distributions (PSD, Sauter mean diameter $d_{32}$), oxide passivation layer thicknesses, water pH, and electrolyte salinities.
- **Thermodynamics & Phase Equilibria:** Computes reaction heat generation ($\approx -16.7\text{ MJ/kg Al}$) and integrates the *Antoine Equation* to predict gas-phase humidity and calculate downstream hydrogen purity ($y_{\text{H2}}$).
- **Non-Linear Optimization:** Employs `scipy.optimize` routines to dynamically solve for optimal feedstock feed rates, water-to-aluminum ratios, and temperature controls to minimize hydrogen cost (LCOH) or maximize energy output.
- **ASME Compliance Engineering:** Formulates ASME Section VIII Division 1 vessel sizing calculations for cylindrical shells and ellipsoidal heads under high operating pressures.
- **Industrial PLC Integration:** Models PEM fuel cell polarization and cooling loops, complete with virtual PID control loops and Kalman signal filters.
- **RESTful Automation (API):** Exposes all engineering models via high-throughput web routes for automated remote operation.

---

## 🔬 Technology Foundation

- **Core Technology:** Patented Aluminum-Water Reaction (AWR) System
- **Efficiency:** 96% hydrogen reaction efficiency (Springer Nature validated)
- **Publication:** DOI 10.1007/s11696-025-04238-7 (Chemical Papers, 2025)
- **Patents:** 2 national + 2 PCT applications filed

**Institutional Recognition:**
- 🏦 **World Bank SOGREEN Grant** (Awarded & Contracted, Q1 2026)
- 🇪🇺 **EU Commission Seal of Excellence** (Hyber Project 101310755)
- 🇹🇷 **TÜBİTAK Active Collaboration** (1507 Product Development)

---

## 📦 Project Structure

```
ReactoN/
├── reacton/
│   ├── __init__.py
│   ├── core/
│   │   ├── thermodynamic_models.py       # AWR Shrinking Core Model kinetics
│   │   ├── parameter_optimizer.py        # SciPy multi-parameter optimization
│   │   └── efficiency_calculator.py      # LHV/HHV and exergy calculations
│   ├── integration/
│   │   ├── industrial_systems.py         # PEM fuel cell & cooling HX models
│   │   ├── control_interface.py          # Real-time PID & SCADA controls
│   │   └── data_acquisition.py           # Telemetry simulator & Kalman filter
│   ├── api/
│   │   ├── schemas.py                    # Pydantic data schemas
│   │   └── server.py                     # FastAPI web automation service
│   ├── compliance/
│   │   ├── safety_analyzer.py            # safety limits (LEL, runaway)
│   │   ├── regulatory_calcs.py           # ASME Section VIII & ISO 16110
│   │   └── reporting.py                  # Engineering report generator
│   └── utils/
│       ├── data_processing.py            # Unit conversions
│       ├── visualization.py              # Matplotlib visual plotters
│       └── logging.py                    # JSON structured logging
├── tests/
│   ├── test_thermodynamics.py
│   ├── test_optimization.py
│   ├── test_integration.py
│   └── test_api.py
├── docs/
│   ├── API.md                            # Mathematical & API documentation
│   ├── INSTALLATION.md                   # Installation & dependency guide
│   ├── TUTORIAL.md                       # Developer tutorial
│   └── SAFETY.md                         # Hydrogen chemical safety guidelines
├── examples/
│   ├── basic_analysis.py                 # Basic feedstock analysis example
│   ├── multi_feedstock_modeling.py       # Comparative feedstock/promoter run
│   └── industrial_integration.py         # Full closed-loop SCADA to report run
├── requirements.txt
├── setup.py
├── LICENSE
└── CONTRIBUTING.md
```

---

## 🚀 Current Status (May 2026)

| Milestone | Status | Target |
|-----------|--------|--------|
| **TRL 4** | ✅ Complete | Lab validated |
| **Core Software Architecture** | 🔄 In Progress | June 2026 |
| **Integration Testing** | 🔄 In Progress | July 2026 |
| **Open Source Release** | ⏳ Planned | August 2026 |
| **Documentation Completion** | ⏳ Planned | August 2026 |
| **TRL 5 Field Demonstration** | ⏳ Planned | September 2026 |

---

## 💻 Development Setup (For Contributors)

```bash
# Clone repository
git clone https://github.com/asrhur/ReactoN.git
cd ReactoN

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Run tests
pytest tests/ -v
```

---

## 📡 Remote Automation via API

ReactoN includes an automated FastAPI service. To start the local server:
```bash
uvicorn reacton.api.server:app --host 127.0.0.1 --port 8000 --reload
```
Once started, you can access the interactive OpenAPI documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to connect external PLCs, SCADA databases, or dashboard integrations.

---

## 👥 Authors & Team

**ASRHÜR Kimya ve Makina Sanayi A.Ş.**

- **Doğukan Ünal** — Chief Scientist & Co-founder
  - 15+ years hydrogen chemistry & electrolyzer R&D
  - Lead author: Springer Nature AWR publication
  - LinkedIn: [Doğukan Ünal](https://www.linkedin.com/in/dogukanunal)

- **Hakan Aras** — Chief Strategy Officer & Co-founder
  - 13+ years EU project management & funding
  - LinkedIn: [Hakan Aras](https://www.linkedin.com/in/hakan-aras/)

---

## 📞 Contact & Support

- **Website:** https://asrhur.com
- **Email:** invest@asrhur.com | dogukan@asrhur.com
- **Phone:** +90 850 885 1444
- **Location:** Ankara, Turkey
