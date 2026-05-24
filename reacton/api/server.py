"""
FastAPI Server providing remote automation APIs for ReactoN.

Exposes computational thermodynamic simulation, parameter optimization, 
and ASME Section VIII vessel wall thickness calculations.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import (
    SimulationInput,
    SimulationOutput,
    OptimizationInput,
    OptimizationOutput,
    ASMECalculationInput,
    ASMECalculationOutput
)
from ..core.thermodynamic_models import AWRThermodynamicModel
from ..core.parameter_optimizer import AWRParameterOptimizer
from ..compliance.regulatory_calcs import ASMEPressureVesselCalc

app = FastAPI(
    title="ReactoN — API Automation Layer",
    description="Computational engineering, thermodynamics and optimization REST service for ASRHÜR AWR systems.",
    version="0.1.0"
)

# Enable CORS for easy cross-origin SCADA or dashboard connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pre-initialize our core engines
thermo_model = AWRThermodynamicModel()
optimizer = AWRParameterOptimizer(model=thermo_model)

@app.get("/api/v1/health")
def health_check():
    """Verify service status."""
    return {"status": "operational", "version": "0.1.0", "engine": "ReactoN SCM Core"}

@app.post("/api/v1/simulate", response_model=SimulationOutput)
def run_simulation(inputs: SimulationInput):
    """
    Run a dynamic batch AWR reactor simulation with kinetics and thermal tracking.
    """
    try:
        df = thermo_model.simulate_batch_reaction(
            aluminum_mass_kg=inputs.aluminum_mass_kg,
            water_mass_kg=inputs.water_mass_kg,
            d_ox_nm=inputs.d_ox_nm,
            particle_size_mean_um=inputs.particle_size_mean_um,
            particle_size_std_um=inputs.particle_size_std_um,
            pH=inputs.pH,
            water_type=inputs.water_type,
            catalyst_molar=inputs.catalyst_molar,
            reactor_volume_l=inputs.reactor_volume_l,
            cooling_duty_w=inputs.cooling_duty_w,
            initial_temp_c=inputs.initial_temp_c,
            initial_pressure_bar=inputs.initial_pressure_bar,
            dt=inputs.dt,
            max_time_s=inputs.max_time_s
        )
        
        telemetry = df.to_dict(orient="records")
        
        # Calculate brief summary metrics
        max_t = float(df["temperature_c"].max())
        max_p = float(df["pressure_bar"].max())
        total_h2 = float(df["H2_produced_g"].max())
        final_conv = float(df["conversion_fraction"].max())
        
        return {
            "success": True,
            "summary": {
                "max_temperature_c": max_t,
                "max_pressure_bar": max_p,
                "total_hydrogen_produced_g": total_h2,
                "final_conversion_fraction": final_conv
            },
            "telemetry": telemetry
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")

@app.post("/api/v1/optimize", response_model=OptimizationOutput)
def run_optimization(inputs: OptimizationInput):
    """
    Solve multivariable non-linear operating parameter optimization under safety constraints.
    """
    try:
        res = optimizer.optimize(
            objective=inputs.objective,
            feedstock_type=inputs.feedstock_type,
            water_type=inputs.water_type,
            target_purity=inputs.target_purity,
            max_pressure_bar=inputs.max_pressure_bar,
            max_temp_c=inputs.max_temp_c
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization solver error: {str(e)}")

@app.post("/api/v1/compliance/asme", response_model=ASMECalculationOutput)
def check_asme_compliance(inputs: ASMECalculationInput):
    """
    Calculate minimum shell and head wall thicknesses under ASME Section VIII specifications.
    """
    try:
        calc = ASMEPressureVesselCalc()
        res = calc.calculate_thicknesses(
            design_pressure_bar=inputs.design_pressure_bar,
            inside_radius_mm=inputs.reactor_radius_mm,
            allowable_stress_mpa=inputs.allowable_stress_mpa,
            joint_efficiency=inputs.joint_efficiency,
            corrosion_allowance_mm=inputs.corrosion_allowance_mm
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ASME calculation error: {str(e)}")
