"""
Unit tests for core thermodynamics and reaction kinetics.
"""

import pytest
import numpy as np
from reacton.core.thermodynamic_models import AWRThermodynamicModel

def test_sauter_mean_diameter():
    model = AWRThermodynamicModel()
    # Log-normal Sauter mean test
    log_mean = np.log(20.0)
    log_std = 0.2
    d32 = model.calculate_sauter_mean_diameter(log_mean, log_std)
    assert d32 > 20e-6  # d32 > mode for positive std
    assert d32 < 100e-6

def test_induction_time():
    model = AWRThermodynamicModel()
    # Dissolution rate should be faster at higher temperatures and higher pH
    t_ind_slow = model.calculate_induction_time(d_ox_nm=3.0, temp_c=25.0, pH=11.0)
    t_ind_fast = model.calculate_induction_time(d_ox_nm=3.0, temp_c=60.0, pH=13.0)
    assert t_ind_fast < t_ind_slow
    assert t_ind_fast >= 0.0

def test_antoine_vapor_pressure():
    model = AWRThermodynamicModel()
    # Water saturation pressure tests
    p_sat_25 = model.calculate_antoine_vapor_pressure(25.0)
    p_sat_100 = model.calculate_antoine_vapor_pressure(100.0)
    
    # 25 °C saturation is roughly 0.031 bar
    assert p_sat_25 == pytest.approx(0.0316, abs=0.01)
    # 100 °C saturation is roughly 1.013 bar
    assert p_sat_100 == pytest.approx(1.013, abs=0.1)

def test_dry_hydrogen_purity():
    model = AWRThermodynamicModel()
    purity = model.calculate_dry_hydrogen_purity(temp_c=15.0, total_pressure_bar=5.0)
    # P_sat at 15 °C is ~ 0.017 bar. Purity is (5 - 0.017) / 5 ~ 99.66%
    assert purity > 0.99
    assert purity <= 1.0

def test_kinetics_step():
    model = AWRThermodynamicModel()
    # At alpha = 0.0, the rate must be positive
    new_alpha, rate = model.calculate_kinetics_step(
        alpha=0.0,
        R0_m=20e-6,
        temp_c=50.0,
        pH=12.0,
        water_type='tap',
        catalyst_molar=0.1,
        dt=1.0
    )
    assert new_alpha > 0.0
    assert rate > 0.0
    
    # Complete conversion limit
    final_alpha, final_rate = model.calculate_kinetics_step(
        alpha=1.0,
        R0_m=20e-6,
        temp_c=50.0,
        pH=12.0,
        water_type='tap',
        catalyst_molar=0.1,
        dt=1.0
    )
    assert final_alpha == 1.0
    assert final_rate == 0.0
