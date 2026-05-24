"""
Pydantic data schemas for FastAPI input validation and response serialization.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class SimulationInput(BaseModel):
    aluminum_mass_kg: float = Field(..., gt=0, description="Active aluminum feedstock mass in kg")
    water_mass_kg: float = Field(..., gt=0, description="Added liquid water mass in kg")
    d_ox_nm: float = Field(3.0, ge=0, description="Initial Al2O3 oxide layer thickness in nanometers")
    particle_size_mean_um: float = Field(25.0, gt=0, description="Mean particle diameter in microns")
    particle_size_std_um: float = Field(5.0, ge=0, description="Standard deviation of particle diameter")
    pH: float = Field(12.5, ge=1, le=14, description="Reactor liquid water pH value")
    water_type: str = Field("tap", description="Water type: 'pure', 'tap', or 'sea'")
    catalyst_molar: float = Field(0.1, ge=0, description="Dissolved alkali (NaOH/KOH) promoter concentration in M")
    reactor_volume_l: float = Field(5.0, gt=0, description="Reactor physical inner volume in Liters")
    cooling_duty_w: float = Field(200.0, ge=0, description="External chilling loop heat transfer capacity in Watts")
    initial_temp_c: float = Field(25.0, ge=0, description="Initial temperature in °C")
    initial_pressure_bar: float = Field(1.0, ge=0, description="Initial internal gas pressure in bar")
    dt: float = Field(1.0, gt=0, le=10.0, description="Simulation timestep in seconds")
    max_time_s: float = Field(600.0, gt=0, le=3600.0, description="Simulation timeout limit in seconds")

class SimulationTelemetryRow(BaseModel):
    time_s: float
    conversion_fraction: float
    reaction_rate_1_s: float
    temperature_c: float
    pressure_bar: float
    p_H2_bar: float
    p_H2O_bar: float
    H2_produced_g: float
    heat_generation_w: float
    in_induction: bool
    induction_time_s: float

class SimulationOutput(BaseModel):
    success: bool
    summary: Dict[str, float]
    telemetry: List[SimulationTelemetryRow]

class OptimizationInput(BaseModel):
    objective: str = Field("maximize_h2_rate", description="Objective: 'maximize_h2_rate', 'minimize_lcoh', 'maximize_exergy'")
    feedstock_type: str = Field("premium", description="Al powder grade: 'premium' or 'recycled'")
    water_type: str = Field("tap", description="Water type: 'pure', 'tap', or 'sea'")
    target_purity: float = Field(0.999, ge=0.5, le=1.0, description="Target minimum hydrogen dry mole fraction")
    max_pressure_bar: float = Field(16.0, gt=1.0, description="Vessel maximum operating pressure limits in bar")
    max_temp_c: float = Field(95.0, gt=30.0, description="Vessel thermal ceiling in °C")

class OptimizationOutput(BaseModel):
    success: bool
    status_message: str
    optimal_parameters: Dict[str, float]
    metrics: Dict[str, float]

class ASMECalculationInput(BaseModel):
    design_pressure_bar: float = Field(..., gt=0, description="Internal design gauge pressure in bar")
    reactor_radius_mm: float = Field(..., gt=0, description="Vessel inside radius in mm")
    allowable_stress_mpa: float = Field(138.0, gt=0, description="Max allowable material stress in MPa (e.g. 316SS at 150°C)")
    joint_efficiency: float = Field(0.85, gt=0, le=1.0, description="Joint efficiency welding factor (0.7 to 1.0)")
    corrosion_allowance_mm: float = Field(1.5, ge=0, description="Vessel wall corrosion allowance in mm")

class ASMECalculationOutput(BaseModel):
    vessel_inside_diameter_mm: float
    allowable_stress_psi: float
    calculated_shell_thickness_mm: float
    calculated_head_thickness_mm: float
