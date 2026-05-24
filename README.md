# ReactoN: Computational Analysis Platform for AWR Systems

**Status:** TRL 4 (Laboratory-Validated) | **Funding:** World Bank SOGREEN | **Recognition:** EU Seal of Excellence

---

## Overview

ReactoN is an advanced, physics- and chemistry-grounded computational analysis and integration platform for ASRHÜR's patented aluminum-water reaction (AWR) hydrogen generation technology.

Designed to serve as the software bridge between laboratory science (TRL 4) and field-validated industrial deployment (TRL 5), ReactoN models raw reaction kinetics, phase equilibria, and pressure vessel sizing, and optimizes multi-criteria operating parameters. It exposes these core computational routines via a high-performance, automated **FastAPI** web service.

---

## Technical Background

The computational platform is built directly upon the physical chemistry, thermodynamics, and kinetics of the AWR process:
$$2\text{Al}(s) + 6\text{H}_2\text{O}(l) \rightarrow 2\text{Al(OH)}_3(s) + 3\text{H}_2(g) + \Delta H_{\text{rxn}}$$
where the reaction is strongly exothermic ($\Delta H_{\text{rxn}} \approx -832\text{ kJ/mol Al}$ or $\approx -16.7\text{ MJ/kg Al}$).

### 1. Solid-Liquid Kinetics (Shrinking Core Model)
To simulate reaction rates of spherical aluminum particles of Sauter mean radius ($R_0$), ReactoN implements the **Shrinking Core Model (SCM)**. The overall conversion fraction ($\alpha \in [0, 1]$) is modeled as a function of time ($t$):
-   **Chemical Reaction Controlled Regime:**
    $$t = \tau_{rxn} \left[ 1 - (1-\alpha)^{1/3} \right], \quad \tau_{rxn} = \frac{\rho_m R_0}{k_{rxn} C_b}$$
-   **Porous Ash Layer Diffusion Controlled Regime:**
    $$t = \tau_{diff} \left[ 1 - 3(1-\alpha)^{2/3} + 2(1-\alpha) \right], \quad \tau_{diff} = \frac{\rho_m R_0^2}{6 D_e C_b}$$
-   **Arrhenius Activation:**
    $$k_{rxn}(T, \text{pH}) = A \cdot \exp\left(-\frac{E_a}{R T_{rxn}}\right) \cdot \left[OH^-\right]^n$$

### 2. Saturated Gas Phase Equilibrium
The generated gas is a mixture of hydrogen and water vapor. Saturation vapor pressure ($P_{sat}$) of water is evaluated via the **Antoine Equation**:
$$\log_{10} P_{sat} (\text{bar}) = A - \frac{B}{T(^\circ\text{C}) + C}$$
*(For water: $A = 5.11564$, $B = 1687.537$, $C = 230.17$)*

This yields the maximum dry hydrogen purity ($y_{H2}$) achievable at the condenser output at temperature $T_{cond}$ and system pressure $P_{total}$:
$$y_{H2} = \frac{P_{total} - P_{sat}(T_{cond})}{P_{total}}$$

---

## Development Challenge

Transitioning AWR technology from **TRL 4 (Laboratory-Validated)** to **TRL 5 (System Prototype in Operational Environment)** introduces critical engineering challenges modeled and resolved by ReactoN:

1.  **Thermal Runaway Mitigation:** Due to high exothermicity, unmanaged batch reactors risk boiling water rapidly or facing structural collapse. ReactoN simulates dynamic heat accumulation ($C_p m \frac{dT}{dt} = Q_{gen} - Q_{cool}$) and uses automated safety loops to trigger emergency shutdowns (ESD) if temperatures exceed $95^\circ\text{C}$ or if the rise rate $dT/dt > 2.5^\circ\text{C/s}$.
2.  **Feedstock & Water Versatility:** The platform must optimize reaction rates for premium pure powders and heavily oxidized recycled Al scrap in tap water, pure water, or seawater (saline pitting corrosion effects).
3.  **Mechanical Structural Integrity:** Pressurized hydrogen reactors require precise mechanical calculations to prevent catastrophic failure. ReactoN implements structural vessel shell and head sizing algorithms using **ASME BPVC Section VIII Division 1** criteria.

---

## Python Architecture

ReactoN features a modular, package-based architecture designed for high-performance scientific simulations and SCADA integration:

```
ReactoN/
├── reacton/
│   ├── __init__.py
│   ├── core/
│   │   ├── thermodynamic_models.py       # SCM kinetics, heat balance, Antoine phase balance
│   │   ├── parameter_optimizer.py        # SciPy SLSQP non-linear multivariable optimizer
│   │   └── efficiency_calculator.py      # LHV/HHV exergy, gravimetric/volumetric density
│   ├── integration/
│   │   ├── industrial_systems.py         # PEM Fuel Cell stack polarization & cooling HX models
│   │   ├── control_interface.py          # Direct-acting cooling loop PID & Virtual PLC
│   │   └── data_acquisition.py           # Gaussian noise telemetry & Kalman signal filters
│   ├── api/
│   │   ├── schemas.py                    # Pydantic data validation schemas
│   │   └── server.py                     # FastAPI REST API web automation service
│   ├── compliance/
│   │   ├── safety_analyzer.py            # Room LEL checks & real-time ESD hazard checks
│   │   ├── regulatory_calcs.py           # ASME cylindrical wall thickness & ISO 16110 checks
│   │   └── reporting.py                  # Automated markdown report generator
│   └── utils/
│       ├── data_processing.py            # Conversions (bar to Pa, SLPM to g/s)
│       ├── visualization.py              # Matplotlib visual plotting engine
│       └── logging.py                    # Structured JSON industrial logger
```

-   **`core/`**: Implements the core physical, chemical, and mathematical solvers.
-   **`integration/`**: Models the downstream fuel cell stack load and simulates a virtual PLC SCADA dashboard.
-   **`api/`**: Exposes the models via RESTful routes to enable automated external PLC/SCADA commands.
-   **`compliance/`**: Formulates ASME Section VIII thickness calculations and audits runs against ISO 16110.

---

## Current Status (May 2026)

| Milestone | Status | Target |
|-----------|--------|--------|
| **TRL 4** | ✅ Complete | Lab validated |
| **Core Software Architecture** | ✅ Complete | June 2026 |
| **Integration Testing** | ✅ Complete | July 2026 |
| **Open Source Release** | ⏳ Planned | August 2026 |
| **Documentation Completion** | ⏳ Planned | August 2026 |
| **TRL 5 Field Demonstration** | ⏳ Planned | September 2026 |

---

## Development Setup (For Contributors)

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

## Remote Automation via API

ReactoN includes an automated FastAPI service. To start the local server:
```bash
uvicorn reacton.api.server:app --host 127.0.0.1 --port 8000 --reload
```
Once started, you can access the interactive OpenAPI documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to connect external PLCs, SCADA databases, or dashboard integrations.

---

## Authors & Team

**ASRHÜR Kimya ve Makina Sanayi A.Ş.**

- **Doğukan Ünal** — Chief Scientist & Co-founder
  - 15+ years hydrogen chemistry & electrolyzer R&D
  - Lead author: Springer Nature AWR publication
  - LinkedIn: [Doğukan Ünal](https://www.linkedin.com/in/dogukanunal)

- **Hakan Aras** — Chief Strategy Officer & Co-founder
  - 13+ years EU project management & funding
  - LinkedIn: [Hakan Aras](https://www.linkedin.com/in/hakan-aras/)

---

## Contact & Support

- **Website:** https://asrhur.com
- **Email:** invest@asrhur.com | dogukan@asrhur.com
- **Phone:** +90 850 885 1444
- **Location:** Ankara, Turkey
