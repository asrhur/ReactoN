"""
Efficiency metrics calculator for AWR systems.

Computes LHV/HHV yield efficiency, volumetric/gravimetric system capacity, exergy 
efficiency, and greenhouse gas offset relative to industrial baselines.
"""

from typing import Dict
from .thermodynamic_models import AWRThermodynamicModel

class AWREfficiencyCalculator:
    """
    Thermodynamic efficiency and CO2 footprint metric engine.
    
    Provides:
    - Gravimetric capacity (wt% H2)
    - Volumetric density (g-H2 / L)
    - HHV/LHV system efficiencies
    - Second-Law Exergy efficiency
    - Carbon offset metrics relative to SMR and fossil electricity
    """
    
    # Heating values of Hydrogen
    LHV_H2 = 120.0e6  # Lower Heating Value, J/kg
    HHV_H2 = 141.8e6  # Higher Heating Value, J/kg
    
    # Specific exergy values (J/kg)
    Ex_Al = 29.0e6   # Exergy of pure Aluminum metal ~ 29 MJ/kg
    Ex_H2 = 117.0e6  # Exergy of Hydrogen ~ 117 MJ/kg
    
    # Industrial carbon baselines (kg-CO2 / kg-H2)
    CO2_SMR = 9.0     # Steam Methane Reforming baseline
    CO2_GRID = 18.0   # Coal-based grid water electrolysis baseline
    
    def __init__(self, model: AWRThermodynamicModel = None):
        """Initialize efficiency calculator."""
        self.model = model if model is not None else AWRThermodynamicModel()
        
    def calculate_system_efficiencies(
        self,
        aluminum_mass_kg: float,
        water_mass_kg: float,
        h2_produced_g: float,
        parasitic_energy_j: float = 0.0
    ) -> Dict[str, float]:
        """
        Calculate gravimetric capacities, volumetric densities, and first/second law efficiencies.
        
        Args:
            aluminum_mass_kg: Active Aluminum mass (kg).
            water_mass_kg: Total water mass added to reactor (kg).
            h2_produced_g: Actual hydrogen gas produced (g).
            parasitic_energy_j: Electrical power spent (cooling, feed motor, PLC) in Joules.
            
        Returns:
            Dictionary containing efficiency indicators.
        """
        h2_produced_kg = h2_produced_g / 1000.0
        
        # 1. Gravimetric capacities
        # Feedstock gravimetric capacity (excluding water, since water can be sourced locally)
        gravimetric_feedstock_wt = (h2_produced_kg / aluminum_mass_kg) * 100.0
        
        # System total gravimetric capacity (including water)
        total_system_mass = aluminum_mass_kg + water_mass_kg
        gravimetric_system_wt = (h2_produced_kg / total_system_mass) * 100.0
        
        # 2. Volumetric density
        # Volumetric capacity based on reactants volume
        vol_al = aluminum_mass_kg / (self.model.rho_Al / 1000.0)  # L
        vol_water = water_mass_kg  # L (density ~ 1kg/L)
        total_reactants_vol_l = vol_al + vol_water
        volumetric_capacity_g_l = h2_produced_g / total_reactants_vol_l
        
        # 3. LHV & HHV yields
        # Lower Heating Value system efficiency (eta = LHV_H2 * m_H2 / (Ex_Al * m_Al + parasitic_energy))
        energy_out_lhv = h2_produced_kg * self.LHV_H2
        energy_out_hhv = h2_produced_kg * self.HHV_H2
        
        # Al primary chemical energy content modeled using heat of combustion (31 MJ/kg)
        al_combustion_energy = aluminum_mass_kg * 31.0e6  # J
        energy_in = al_combustion_energy + parasitic_energy_j
        
        lhv_efficiency = energy_out_lhv / energy_in if energy_in > 0 else 0.0
        hhv_efficiency = energy_out_hhv / energy_in if energy_in > 0 else 0.0
        
        # 4. Exergy (Second Law) Efficiency
        # eta_ex = Ex_H2 * m_H2 / (Ex_Al * m_Al + parasitic_energy)
        exergy_in = (aluminum_mass_kg * self.Ex_Al) + parasitic_energy_j
        exergy_out = h2_produced_kg * self.Ex_H2
        exergy_efficiency = exergy_out / exergy_in if exergy_in > 0 else 0.0
        
        return {
            "gravimetric_feedstock_capacity_wt": float(gravimetric_feedstock_wt),
            "gravimetric_system_capacity_wt": float(gravimetric_system_wt),
            "volumetric_capacity_g_h2_l": float(volumetric_capacity_g_l),
            "lhv_system_efficiency": float(lhv_efficiency),
            "hhv_system_efficiency": float(hhv_efficiency),
            "second_law_exergy_efficiency": float(exergy_efficiency)
        }
        
    def calculate_environmental_footprint(self, h2_produced_g: float) -> Dict[str, float]:
        """
        Calculate the carbon dioxide offset/reduction achieved by using the on-demand AWR system 
        instead of fossil-based hydrogen generation.
        
        Args:
            h2_produced_g: Hydrogen produced in grams.
            
        Returns:
            Dictionary containing kg-CO2 saved.
        """
        h2_produced_kg = h2_produced_g / 1000.0
        
        # Offset vs Steam Methane Reforming
        co2_smr_offset = h2_produced_kg * self.CO2_SMR
        
        # Offset vs Coal-based Grid Electrolysis
        co2_grid_offset = h2_produced_kg * self.CO2_GRID
        
        return {
            "co2_saved_vs_smr_kg": float(co2_smr_offset),
            "co2_saved_vs_coal_grid_kg": float(co2_grid_offset)
        }
