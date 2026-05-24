"""
Industrial system models integrated with AWR reactors.

Implements a high-fidelity PEM Fuel Cell model (electrochemistry, polarization curves, 
H2 consumption rate) and a counter-flow Cooling Loop Heat Exchanger model.
"""

import numpy as np
from typing import Dict

class PEMFuelCellModel:
    """
    Electrochemical modeling of a Proton Exchange Membrane Fuel Cell (PEMFC) stack.
    
    Models cell polarization curves (Voltage vs. Current Density) by accounting for:
    1. Reversible Nernst Open Circuit Voltage (Voc)
    2. Activation polarization (Tafel equation)
    3. Ohmic losses (membrane and contact resistance)
    4. Concentration/mass transfer losses
    """
    
    # Faraday's constant (C/mol e-)
    F = 96485.33212
    
    def __init__(
        self,
        num_cells: int = 40,
        cell_active_area_cm2: float = 100.0,
        membrane_thickness_um: float = 25.0
    ):
        """
        Initialize PEMFC model.
        
        Args:
            num_cells: Number of cells in series in the stack.
            cell_active_area_cm2: Active electrochemical area per cell.
            membrane_thickness_um: Polymer electrolyte membrane thickness.
        """
        self.num_cells = num_cells
        self.cell_active_area_cm2 = cell_active_area_cm2
        self.membrane_thickness_um = membrane_thickness_um
        
        # Electrochemistry constants
        self.V_open_circuit = 1.15  # Volts (realistic OCV)
        self.alpha_transfer = 0.5   # Charge transfer coefficient
        self.exchange_current_density = 1e-4  # A/cm^2 (typical)
        self.R_contact = 0.05       # Ohm*cm^2 (typical contact resistance)
        self.limiting_current_density = 1.5   # A/cm^2 (maximum mass transport)
        
    def calculate_cell_losses(self, current_density_a_cm2: float, temp_c: float) -> Dict[str, float]:
        """
        Calculate individual cell overpotentials (losses).
        """
        temp_k = temp_c + 273.15
        
        if current_density_a_cm2 <= 0:
            return {"voltage_v": self.V_open_circuit, "v_act": 0.0, "v_ohm": 0.0, "v_conc": 0.0}
            
        # 1. Activation loss (Tafel Equation)
        # V_act = (R * T / (alpha * F)) * ln(i / i_0)
        v_act = (8.314 * temp_k / (self.alpha_transfer * self.F)) * np.log(current_density_a_cm2 / self.exchange_current_density)
        v_act = max(0.0, v_act)
        
        # 2. Ohmic loss
        # R_membrane = thickness / conductivity.
        # Reference conductivity for Nafion ~ 0.1 S/cm.
        conductivity = 0.08 + 0.0005 * temp_c  # S/cm (increases with temp)
        t_cm = self.membrane_thickness_um * 1e-4
        r_membrane = t_cm / conductivity  # Ohm*cm^2
        r_total = r_membrane + self.R_contact
        v_ohm = current_density_a_cm2 * r_total
        
        # 3. Concentration loss
        # V_conc = -B * ln(1 - i / i_L)
        B = 0.05  # Concentration loss parameter
        if current_density_a_cm2 >= self.limiting_current_density:
            v_conc = 1.0  # Cell is flooded / current is too high
        else:
            v_conc = -B * np.log(1.0 - (current_density_a_cm2 / self.limiting_current_density))
            
        # 4. Net Voltage
        voltage = self.V_open_circuit - v_act - v_ohm - v_conc
        voltage = max(0.0, voltage)
        
        return {
            "voltage_v": float(voltage),
            "v_act": float(v_act),
            "v_ohm": float(v_ohm),
            "v_conc": float(v_conc)
        }

    def simulate_stack(self, current_amps: float, temp_c: float = 75.0) -> Dict[str, float]:
        """
        Simulate the fuel cell stack performance at a given current load.
        
        Args:
            current_amps: Electric current load in Amperes.
            temp_c: Fuel cell operating temperature in °C.
            
        Returns:
            Dictionary containing voltage, power, and hydrogen consumption rate.
        """
        current_density = current_amps / self.cell_active_area_cm2
        losses = self.calculate_cell_losses(current_density, temp_c)
        
        cell_v = losses["voltage_v"]
        stack_v = cell_v * self.num_cells
        stack_power_w = stack_v * current_amps
        
        # Hydrogen consumption rate via Faraday's Law
        # Stack consumes: num_cells * I / (2 * F) moles of H2 per second
        # (Since H2 -> 2H+ + 2e-)
        moles_h2_per_sec = (self.num_cells * current_amps) / (2.0 * self.F)
        h2_consumption_g_s = moles_h2_per_sec * 2.016
        
        return {
            "stack_voltage_v": float(stack_v),
            "current_amps": float(current_amps),
            "power_output_w": float(stack_power_w),
            "h2_consumption_g_s": float(h2_consumption_g_s),
            "cell_voltage_v": float(cell_v),
            "v_act_loss": float(losses["v_act"]),
            "v_ohm_loss": float(losses["v_ohm"]),
            "v_conc_loss": float(losses["v_conc"])
        }

class CoolingLoopModel:
    """
    Models an active counter-flow heat exchanger (HX) for the reactor cooling loop.
    
    Q = U * A * LMTD
    LMTD = (dT1 - dT2) / ln(dT1 / dT2)
    """
    
    def __init__(self, overall_u_w_m2k: float = 800.0, area_m2: float = 0.15):
        """
        Initialize cooling loop heat exchanger.
        
        Args:
            overall_u_w_m2k: Heat transfer coefficient in W/(m^2*K).
            area_m2: Heat exchange surface area in m^2.
        """
        self.U = overall_u_w_m2k
        self.A = area_m2
        
    def calculate_heat_dissipation(
        self,
        reactor_temp_c: float,
        coolant_inlet_temp_c: float,
        coolant_flow_rate_l_min: float
    ) -> float:
        """
        Calculate actual cooling duty in Watts.
        
        Args:
            reactor_temp_c: Current reactor temperature.
            coolant_inlet_temp_c: Cooling water supply temperature.
            coolant_flow_rate_l_min: Coolant flow rate.
            
        Returns:
            Cooling capacity in Watts.
        """
        if coolant_flow_rate_l_min <= 0 or reactor_temp_c <= coolant_inlet_temp_c:
            return 0.0
            
        # Mass flow rate of cooling water (kg/s)
        m_dot_coolant = (coolant_flow_rate_l_min / 60.0) * 1.0  # density ~ 1kg/L
        
        # Max theoretical heat transfer: Q_max = m_dot * Cp * (T_rxn - T_cool_in)
        Cp_water = 4184.0  # J/kgK
        q_max = m_dot_coolant * Cp_water * (reactor_temp_c - coolant_inlet_temp_c)
        
        # Effectiveness-NTU method approximation for liquid-liquid counter-flow HX
        # NTU = U * A / (m_dot * Cp)
        NTU = (self.U * self.A) / (m_dot_coolant * Cp_water)
        effectiveness = (1 - np.exp(-NTU))  # simple single-stream limit
        
        q_actual = effectiveness * q_max
        return float(q_actual)
