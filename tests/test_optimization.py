"""
Unit tests for optimization and efficiency calculation.
"""

import pytest
from reacton.core.parameter_optimizer import AWRParameterOptimizer
from reacton.core.efficiency_calculator import AWREfficiencyCalculator

def test_efficiency_calculator():
    calc = AWREfficiencyCalculator()
    effs = calc.calculate_system_efficiencies(
        aluminum_mass_kg=1.0,
        water_mass_kg=4.0,
        h2_produced_g=100.0,
        parasitic_energy_j=1000.0
    )
    assert effs["gravimetric_feedstock_capacity_wt"] == pytest.approx(10.0, rel=1e-3)
    assert effs["gravimetric_system_capacity_wt"] == pytest.approx(2.0, rel=1e-3)
    assert effs["second_law_exergy_efficiency"] > 0.0
    assert effs["lhv_system_efficiency"] > 0.0

def test_environmental_offsets():
    calc = AWREfficiencyCalculator()
    offsets = calc.calculate_environmental_footprint(h2_produced_g=1000.0)  # 1 kg H2
    assert offsets["co2_saved_vs_smr_kg"] == 9.0
    assert offsets["co2_saved_vs_coal_grid_kg"] == 18.0

def test_optimizer_flow_rate():
    optimizer = AWRParameterOptimizer()
    res = optimizer.optimize(
        objective='maximize_h2_rate',
        target_purity=0.99,
        max_pressure_bar=10.0
    )
    assert res["success"] is True
    assert "optimal_parameters" in res
    assert res["optimal_parameters"]["reactor_pressure_bar"] >= 1.0
    assert res["optimal_parameters"]["reactor_pressure_bar"] <= 10.0
    assert res["metrics"]["hydrogen_flow_rate_slpm"] > 0.0

def test_optimizer_lcoh():
    optimizer = AWRParameterOptimizer()
    res = optimizer.optimize(
        objective='minimize_lcoh',
        feedstock_type='recycled',
        target_purity=0.999
    )
    assert res["success"] is True
    assert res["metrics"]["levelized_cost_usd_kg"] > 0.0
