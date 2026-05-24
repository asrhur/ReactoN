"""
Thermodynamic and chemical kinetics modeling for aluminum-water reaction (AWR) system.

This module implements the Shrinking Core Model (SCM) to evaluate reaction rates under
varying feedstock configurations, water qualities, and environmental conditions.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, List, Any

class AWRThermodynamicModel:
    """
    Aluminum-Water Reaction (AWR) Thermodynamic and Kinetics Model.
    
    Reaction: 2Al(s) + 6H2O(l) -> 2Al(OH)3(s) + 3H2(g) + Heat
    
    This class models:
    1. Solid-liquid kinetics using the Shrinking Core Model (SCM).
    2. Log-normal particle size distributions.
    3. Passive oxide layer induction times.
    4. Salinity (Cl-) and pH kinetic activation.
    5. Non-isothermal heat balance.
    6. Vapor-liquid equilibrium using Antoine's equation for gas purity.
    """
    
    # Physical and thermodynamic constants
    R = 8.314462618  # Ideal Gas Constant, J/(mol*K)
    rho_Al = 2700.0  # Density of Aluminum, kg/m^3
    MW_Al = 0.02698  # Molar Mass of Aluminum, kg/mol
    MW_H2 = 0.002016  # Molar Mass of Hydrogen, kg/mol
    MW_H2O = 0.018015  # Molar Mass of Water, kg/mol
    MW_AlOH3 = 0.07800  # Molar Mass of Aluminum Hydroxide, kg/mol
    
    delta_H_rxn = -832000.0  # Enthalpy of reaction, J/mol Al (-16.7 MJ/kg Al)
    Cp_water = 4184.0  # Specific heat capacity of liquid water, J/(kg*K)
    Cp_Al = 900.0  # Specific heat capacity of Aluminum, J/(kg*K)
    Cp_vessel = 500.0  # Reference specific heat capacity of metal vessel (steel), J/(kg*K)
    
    # Reference conditions
    T_ref = 298.15  # 25 °C in Kelvin
    P_ref = 1.01325  # Atmospheric pressure in bar
    
    # Kinetic parameters (Default values based on literature for NaOH/KOH activation)
    Ea = 65000.0  # Activation Energy, J/mol
    A_rxn = 1.2e5  # Pre-exponential factor, m/(s * M^n)
    n_pH = 0.5  # Reaction order with respect to OH- concentration
    De_ref = 1.0e-11  # Reference effective diffusion coefficient through porous ash layer, m^2/s
    Ea_diff = 40000.0  # Activation energy for diffusion, J/mol
    
    def __init__(self, vessel_mass_kg: float = 15.0):
        """
        Initialize the AWR Thermodynamic and Kinetics Model.
        
        Args:
            vessel_mass_kg: Mass of the reactor vessel (for thermal mass inertia calculation).
        """
        self.vessel_mass_kg = vessel_mass_kg

    def calculate_sauter_mean_diameter(self, log_mean: float, log_std: float) -> float:
        """
        Calculate the Sauter mean diameter (d32) of a log-normal particle size distribution.
        
        For a log-normal distribution, d32 is given by:
        d32 = exp(mu + 2.5 * sigma^2)
        
        Args:
            log_mean: Mean of the log of the particle size (ln of microns).
            log_std: Standard deviation of the log of the particle size (ln of microns).
            
        Returns:
            Sauter mean diameter in meters.
        """
        d32_microns = np.exp(log_mean + 2.5 * (log_std ** 2))
        return d32_microns * 1e-6

    def calculate_induction_time(self, d_ox_nm: float, temp_c: float, pH: float) -> float:
        """
        Calculate the induction time (t_ind) in seconds required to dissolve the 
        passive aluminum oxide (Al2O3) layer.
        
        The dissolution rate of Al2O3 increases with temperature and alkalinity (pH).
        
        Args:
            d_ox_nm: Thickness of the oxide layer in nanometers (typically 2 to 5 nm).
            temp_c: Reactor temperature in °C.
            pH: Water pH value.
            
        Returns:
            Induction time in seconds.
        """
        temp_k = temp_c + 273.15
        # OH- concentration
        c_OH = 10 ** (pH - 14.0) if pH >= 7.0 else 10 ** (7.0 - 14.0)
        
        # Arrhenius rate for oxide dissolution (activation energy ~ 72 kJ/mol)
        Ea_diss = 72000.0
        A_diss = 8.5e8  # Dissolution constant, nm/(s * M^0.6)
        
        rate_diss = A_diss * np.exp(-Ea_diss / (self.R * temp_k)) * (c_OH ** 0.6)
        
        # Add a minimum dissolution baseline for low pH / low temp
        rate_diss = max(rate_diss, 1e-4)
        
        t_ind = d_ox_nm / rate_diss
        return float(t_ind)

    def calculate_kinetics_step(
        self,
        alpha: float,
        R0_m: float,
        temp_c: float,
        pH: float,
        water_type: str,
        catalyst_molar: float,
        dt: float
    ) -> Tuple[float, float]:
        """
        Solve a single step of the AWR kinetics using the combined Shrinking Core Model (SCM).
        
        Args:
            alpha: Current conversion fraction (0.0 to 1.0).
            R0_m: Particle radius in meters (Sauter mean radius).
            temp_c: Reactor temperature in °C.
            pH: Water pH.
            water_type: 'pure', 'tap', or 'sea'.
            catalyst_molar: Molarity of catalyst/promoter (e.g. NaOH/KOH) in mol/L.
            dt: Timestep in seconds.
            
        Returns:
            Tuple: (new_alpha, dalpha_dt)
        """
        if alpha >= 0.9999:
            return 1.0, 0.0
            
        temp_k = temp_c + 273.15
        
        # Molarity of OH- including dissolved catalyst
        c_OH = 10 ** (pH - 14.0) + catalyst_molar
        c_OH = max(c_OH, 1e-7)
        
        # Chemical reaction rate constant (k_rxn)
        k_rxn = self.A_rxn * np.exp(-self.Ea / (self.R * temp_k)) * (c_OH ** self.n_pH)
        
        # Effective diffusion coefficient (De)
        De = self.De_ref * np.exp(-self.Ea_diff / (self.R * (temp_k - 20)))  # reference offset
        
        # Water quality correction factors (f_water)
        # Seawater contains Cl- ions that trigger pitting corrosion, accelerating breakdown
        # of the passive layer and active reaction. Tap water has slight ions.
        f_water = 1.0
        if water_type == 'sea':
            f_water = 1.25  # Cl- acceleration factor
        elif water_type == 'tap':
            f_water = 1.05
        elif water_type == 'pure':
            f_water = 0.95  # lacking ionic acceleration
            
        k_rxn *= f_water
        De *= f_water
        
        # Reactant bulk concentration (water concentration, modeled as density-based ~ 55.5 mol/L)
        C_b = 55.5e3  # mol/m^3
        
        # Molar density of Aluminum (mol/m^3)
        rho_m = self.rho_Al / self.MW_Al
        
        # Characteristic times for regimes (SCM)
        # Chemical reaction time scale
        tau_rxn = (rho_m * R0_m) / (k_rxn * c_OH)
        # Diffusion ash layer time scale
        tau_diff = (rho_m * (R0_m ** 2)) / (6 * De * C_b)
        
        # Safely compute derivatives using combined regime logic
        # dalpha/dt = 3 * (1-alpha)^(2/3) / [ tau_rxn + tau_diff * 2 * (1 - (1-alpha)^(1/3)) ]
        term_rxn = tau_rxn
        term_diff = 2.0 * tau_diff * (1.0 - (1.0 - alpha) ** (1/3))
        
        denominator = term_rxn + term_diff
        if denominator <= 0:
            dalpha_dt = 0.0
        else:
            dalpha_dt = (3.0 * (1.0 - alpha) ** (2/3)) / denominator
            
        # Water abundance limitation factor (if reaction runs dry, rate drops)
        # (This is handled in the simulator system mass balance)
        
        # Integration (Euler forward with bounds)
        new_alpha = min(alpha + dalpha_dt * dt, 1.0)
        
        return float(new_alpha), float(dalpha_dt)

    def calculate_antoine_vapor_pressure(self, temp_c: float) -> float:
        """
        Calculate the saturation vapor pressure of water using the Antoine Equation.
        
        Antoine Equation: log10(P_sat) = A - B / (T + C)
        
        Args:
            temp_c: Temperature in °C.
            
        Returns:
            Vapor pressure in bar.
        """
        # Clamp temperature to avoid numerical errors
        t = max(0.1, min(temp_c, 370.0))
        A = 5.11564
        B = 1687.537
        C = 230.170
        log_p = A - (B / (t + C))
        p_bar = 10 ** log_p
        return float(p_bar)

    def calculate_dry_hydrogen_purity(self, temp_c: float, total_pressure_bar: float) -> float:
        """
        Calculate the thermodynamic maximum dry hydrogen purity (mole fraction) 
        after condensation at a given condenser temperature and pressure.
        
        y_H2 = (P_total - P_sat(T_cond)) / P_total
        
        Args:
            temp_c: Condenser temperature in °C.
            total_pressure_bar: System pressure in bar.
            
        Returns:
            Purity as a value between 0.0 and 1.0.
        """
        p_sat = self.calculate_antoine_vapor_pressure(temp_c)
        if p_sat >= total_pressure_bar:
            return 0.0  # Gas is 100% steam or system is flooded
        y_H2 = (total_pressure_bar - p_sat) / total_pressure_bar
        return float(y_H2)

    def simulate_batch_reaction(
        self,
        aluminum_mass_kg: float,
        water_mass_kg: float,
        d_ox_nm: float,
        particle_size_mean_um: float,
        particle_size_std_um: float,
        pH: float,
        water_type: str,
        catalyst_molar: float,
        reactor_volume_l: float,
        cooling_duty_w: float,
        initial_temp_c: float = 25.0,
        initial_pressure_bar: float = 1.0,
        dt: float = 1.0,
        max_time_s: float = 3600.0
    ) -> pd.DataFrame:
        """
        Perform a dynamic non-isothermal, pressurized simulation of a batch AWR reactor run.
        
        This models reaksiyon kinetics, thermal balance (exothermic generation vs vessel heat
        capacitance and active cooling), and pressure balance (H2 production + vapor accumulation).
        
        Args:
            aluminum_mass_kg: Active Aluminum mass (kg).
            water_mass_kg: Mass of water inside the reactor (kg).
            d_ox_nm: Aluminum oxide layer thickness (nm).
            particle_size_mean_um: Mean Al particle size in microns.
            particle_size_std_um: Standard deviation of Al particle size (microns).
            pH: Water pH.
            water_type: 'pure', 'tap', or 'sea'.
            catalyst_molar: Catalyst molar concentration (M).
            reactor_volume_l: Volume of reactor vessel (L).
            cooling_duty_w: Heat exchange cooling capacity (W).
            initial_temp_c: Initial temperature (°C).
            initial_pressure_bar: Initial reactor gas pressure (bar).
            dt: Simulation timestep (s).
            max_time_s: Cutoff time (s).
            
        Returns:
            Pandas DataFrame containing reaction telemetry history.
        """
        # Calculate Sauter Mean Radius
        # Log parameters of log-normal distribution
        mu = np.log(particle_size_mean_um)
        sigma = particle_size_std_um / particle_size_mean_um  # approx standard deviation
        R0_m = self.calculate_sauter_mean_diameter(mu, sigma) / 2.0
        
        # Setup states
        time = 0.0
        alpha = 0.0
        temp_c = initial_temp_c
        
        # Calculate total moles of reactable Aluminum
        moles_Al_total = (aluminum_mass_kg * 1000.0) / (self.MW_Al * 1000.0)  # mol
        moles_H2O_total = (water_mass_kg * 1000.0) / (self.MW_H2O * 1000.0)  # mol
        
        # Check stoichiometry: 2 Al reacts with 6 H2O -> 3 H2O per 1 Al
        moles_Al_stoich_limit = moles_H2O_total / 3.0
        active_moles_Al = min(moles_Al_total, moles_Al_stoich_limit)
        
        moles_H2_produced = 0.0
        pressure_bar = initial_pressure_bar
        
        # Induction time counter
        t_induction = self.calculate_induction_time(d_ox_nm, temp_c, pH)
        induction_elapsed = 0.0
        in_induction = True
        
        # History lists
        history: List[Dict[str, Any]] = []
        
        # Calculate thermal masses
        # C_vessel = m_vessel * Cp_vessel
        # C_contents = m_Al * Cp_Al + m_water * Cp_water
        C_thermal_total = (self.vessel_mass_kg * self.Cp_vessel) + \
                          (aluminum_mass_kg * self.Cp_Al) + \
                          (water_mass_kg * self.Cp_water)
        
        gas_volume_m3 = (reactor_volume_l * 1e-3) - (aluminum_mass_kg / self.rho_Al) - (water_mass_kg / 1000.0)
        gas_volume_m3 = max(gas_volume_m3, 1e-5)  # prevent negative gas space
        
        while time <= max_time_s:
            # 1. Check induction/dissolution phase
            if in_induction:
                t_induction = self.calculate_induction_time(d_ox_nm, temp_c, pH)
                induction_elapsed += dt
                if induction_elapsed >= t_induction:
                    in_induction = False
                
                dalpha_dt = 0.0
                q_gen = 0.0
            else:
                # 2. Solve Kinetics Step
                alpha, dalpha_dt = self.calculate_kinetics_step(
                    alpha=alpha,
                    R0_m=R0_m,
                    temp_c=temp_c,
                    pH=pH,
                    water_type=water_type,
                    catalyst_molar=catalyst_molar,
                    dt=dt
                )
                
                # Al consumption rate in moles/second
                moles_Al_consumed_per_s = dalpha_dt * active_moles_Al
                
                # Exothermic heat generation rate (Q_gen = n_dot_Al * delta_H_rxn)
                # Enthalpy is negative (exothermic), so we negate it for heat input
                q_gen = moles_Al_consumed_per_s * (-self.delta_H_rxn)
                
                # Hydrogen production rate (1.5 moles of H2 per mole of Al)
                moles_H2_produced += moles_Al_consumed_per_s * 1.5 * dt
            
            # 3. Thermal Balance
            # dT/dt = (Q_gen - Q_cooling) / C_thermal_total
            # Clamp cooling so we don't cool below ambient
            effective_cooling = min(cooling_duty_w, q_gen + 100.0) if temp_c > initial_temp_c else 0.0
            dT_dt = (q_gen - effective_cooling) / C_thermal_total
            temp_c += dT_dt * dt
            temp_c = max(initial_temp_c, temp_c)  # Clamp to ambient baseline
            
            # 4. Gas Phase Pressure Balance
            # moles of H2 in gas space
            temp_k = temp_c + 273.15
            # Ideal gas pressure of hydrogen: P_H2 = n_H2 * R * T / V_gas
            P_H2_pa = (moles_H2_produced * self.R * temp_k) / gas_volume_m3
            P_H2_bar = P_H2_pa * 1e-5
            
            # Antoine water vapor pressure
            P_sat_bar = self.calculate_antoine_vapor_pressure(temp_c)
            
            # Total pressure
            pressure_bar = P_H2_bar + P_sat_bar
            
            # 5. Output record
            history.append({
                "time_s": time,
                "conversion_fraction": alpha,
                "reaction_rate_1_s": dalpha_dt,
                "temperature_c": temp_c,
                "pressure_bar": pressure_bar,
                "p_H2_bar": P_H2_bar,
                "p_H2O_bar": P_sat_bar,
                "H2_produced_g": moles_H2_produced * (self.MW_H2 * 1000.0),
                "heat_generation_w": q_gen,
                "in_induction": in_induction,
                "induction_time_s": t_induction
            })
            
            # End conditions
            if alpha >= 0.999:
                break
                
            time += dt
            
        return pd.DataFrame(history)
