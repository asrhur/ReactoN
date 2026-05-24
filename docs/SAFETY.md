# ReactoN Hydrogen Safety & Handling Guidelines

Hydrogen is a highly flammable gas requiring rigorous safety protocols during storage, generation, and integration. This document details the key safety parameters, explosion thresholds, and reactor mitigation guidelines modeled within the **ReactoN** platform.

---

## ⚡ Chemical Safety Thresholds

### 1. Flammability Limits (Explosive Range)
Hydrogen has exceptionally wide flammability limits in air at standard atmospheric conditions:
-   **Lower Explosive Limit (LEL):** **4.0 vol%**
-   **Upper Explosive Limit (UEL):** **75.0 vol%**
-   **Minimum Ignition Energy:** **0.02 mJ** (Extremely sensitive to static discharge and sparks).

#### Ventilation Requirements:
Enclosures housing AWR reactors must maintain active ventilation. Under **ISO 16110**, mechanical air exchange rates should keep steady-state hydrogen concentrations below **25% of the LEL** (i.e. $< 1.0\text{ vol\%}$) during standard operating leakage conditions.

---

## 🛡️ Reactor Operational Safety

### 1. Thermal Runaway Mitigation
The AWR reaction is strongly exothermic ($\Delta H_{\text{rxn}} \approx -16.7\text{ MJ/kg Al}$). If reactor core temperature rises above $95^\circ\text{C}$ or if the temperature rate of change ($dT/dt$) exceeds $2.5^\circ\text{C/s}$, the automated system must trigger a high-priority **Emergency Shutdown (ESD)** signal:
1.  **Stop raw feedstock feeding immediately.**
2.  **Fully open secondary coolant valves.**
3.  **Initiate inert nitrogen (N2) sweep gas injection (if available) to dilute and inert the headspace.**

### 2. Overpressure Management
All pressurized AWR installations must be equipped with mechanical spring-loaded **Pressure Relief Valves (PRV)** set to activate at the vessel maximum design pressure ($P_{design}$). The API will flag critical overpressure warnings when current pressures exceed $80\%$ of $P_{design}$, prompting SCADA operators to open relief venting solenoids.

### 3. Air Ingress & Oxygen Prevention
To prevent forming explosive mixtures within the reactor headspace, air must be purged using vacuum cycles or nitrogen sweeps before starting feedstock feeding. Kepala gas oxygen fractions must remain below the **Limiting Oxygen Concentration (LOC)** of **5.0 vol%**.
